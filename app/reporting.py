from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict
from zoneinfo import ZoneInfo

from .reservations import list_reservations, Reservation
from .timezone_utils import now_hotel, to_hotel_tz


def daily_checkin_list(reservations_path: Path, date_str: str, hotel_tz: ZoneInfo) -> List[Reservation]:
    """
    Return check-ins for a given date, excluding invalid reservations where check-in >= check-out.
    
    Args:
        reservations_path: Path to reservations (CSV or SQLite database)
        date_str: Date in YYYY-MM-DD format (interpreted as midnight in hotel timezone)
        hotel_tz: ZoneInfo object for hotel timezone
        
    Returns:
        List of Reservation objects with check-in on the specified date
    """
    # Check if using SQLite backend
    if reservations_path.suffix == '.db':
        import sqlite3
        conn = sqlite3.connect(str(reservations_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, room_id, guest_name, guest_phone, guest_email,
                   start_date, end_date, num_guests, status, total_cost,
                   created_at, updated_at
            FROM reservations
            WHERE start_date = ?
              AND start_date < end_date
              AND status IN ('Confirmed', 'Checked-In')
            ORDER BY room_id
        """, (date_str,))
        
        reservations = []
        for row in cursor.fetchall():
            reservations.append(Reservation(
                reservation_id=row[0],
                room_id=row[1],
                guest_name=row[2],
                phone=row[3],
                email=row[4],
                check_in_date=row[5],
                check_out_date=row[6],
                num_guests=row[7],
                status=row[8],
                total_cost=row[9],
                created_at=row[10],
                updated_at=row[11]
            ))
        
        conn.close()
        return reservations
    else:
        # CSV backend
        rs = list_reservations(reservations_path)
        valid = []
        for r in rs:
            # Skip invalid reservations (check-in must be before check-out)
            if r.check_in_date >= r.check_out_date:
                continue
            if r.check_in_date == date_str and r.status in {"Confirmed", "Checked-In"}:
                valid.append(r)
        return valid


def daily_checkout_list(reservations_path: Path, date_str: str, hotel_tz: ZoneInfo) -> List[Reservation]:
    """
    Return check-outs for a given date, excluding invalid reservations where check-in >= check-out.
    
    Args:
        reservations_path: Path to reservations (CSV or SQLite database)
        date_str: Date in YYYY-MM-DD format (interpreted as midnight in hotel timezone)
        hotel_tz: ZoneInfo object for hotel timezone
        
    Returns:
        List of Reservation objects with check-out on the specified date
    """
    # Check if using SQLite backend
    if reservations_path.suffix == '.db':
        import sqlite3
        conn = sqlite3.connect(str(reservations_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, room_id, guest_name, guest_phone, guest_email,
                   start_date, end_date, num_guests, status, total_cost,
                   created_at, updated_at
            FROM reservations
            WHERE end_date = ?
              AND start_date < end_date
              AND status IN ('Checked-In', 'Checked-Out', 'Cancelled')
            ORDER BY room_id
        """, (date_str,))
        
        reservations = []
        for row in cursor.fetchall():
            reservations.append(Reservation(
                reservation_id=row[0],
                room_id=row[1],
                guest_name=row[2],
                phone=row[3],
                email=row[4],
                check_in_date=row[5],
                check_out_date=row[6],
                num_guests=row[7],
                status=row[8],
                total_cost=row[9],
                created_at=row[10],
                updated_at=row[11]
            ))
        
        conn.close()
        return reservations
    else:
        # CSV backend
        rs = list_reservations(reservations_path)
        valid = []
        for r in rs:
            # Skip invalid reservations (check-in must be before check-out)
            if r.check_in_date >= r.check_out_date:
                continue
            if r.check_out_date == date_str and r.status in {"Checked-In", "Checked-Out", "Cancelled"}:
                valid.append(r)
        return valid


def monthly_revenue_summary(reservations_path: Path, year_month: str) -> float:
    """
    Calculate monthly revenue based on check-out dates.
    
    Args:
        reservations_path: Path to reservations (CSV or SQLite database)
        year_month: Month in YYYY-MM format
        
    Returns:
        Total revenue for the month
    """
    # Check if using SQLite backend
    if reservations_path.suffix == '.db':
        import sqlite3
        conn = sqlite3.connect(str(reservations_path))
        cursor = conn.cursor()
        
        # Query for reservations with check-out dates in the specified month
        cursor.execute("""
            SELECT SUM(total_cost)
            FROM reservations
            WHERE end_date LIKE ? || '%'
        """, (year_month,))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        return round(result if result else 0.0, 2)
    else:
        # CSV backend
        res = 0.0
        rs = list_reservations(reservations_path)
        for r in rs:
            if r.check_out_date.startswith(year_month):
                res += float(r.total_cost)
        return round(res, 2)


def compute_nights(check_in_date: str, check_out_date: str) -> int:
    """
    Compute number of nights from check-in to check-out date.
    
    Args:
        check_in_date: Date in YYYY-MM-DD format
        check_out_date: Date in YYYY-MM-DD format
        
    Returns:
        Number of nights (days difference)
        
    Note:
        Uses naive datetime objects since we only need date difference,
        not timezone-aware calculations. Date strings are already in
        hotel timezone from the UI.
    """
    start = datetime.strptime(check_in_date, "%Y-%m-%d")
    end = datetime.strptime(check_out_date, "%Y-%m-%d")
    return (end - start).days


def guest_reservation_detail_report(reservations_path: Path, start_date: str, end_date: str) -> List[Reservation]:
    """
    Generate detailed report of reservations within date range.
    Includes all reservations that overlap the specified period:
    - Check-in before or during the period, AND
    - Check-out during or after the start of the period
    Returns list sorted by check_in_date ascending.
    
    Args:
        reservations_path: Path to reservations (CSV or SQLite database)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    # Check if using SQLite backend
    if reservations_path.suffix == '.db':
        import sqlite3
        conn = sqlite3.connect(str(reservations_path))
        cursor = conn.cursor()
        
        # Query for reservations that overlap the date range
        cursor.execute("""
            SELECT id, room_id, guest_name, guest_phone, guest_email,
                   start_date, end_date, num_guests, status, total_cost,
                   created_at, updated_at
            FROM reservations
            WHERE start_date <= ? AND end_date >= ?
            ORDER BY start_date
        """, (end_date, start_date))
        
        reservations = []
        for row in cursor.fetchall():
            reservations.append(Reservation(
                reservation_id=row[0],
                room_id=row[1],
                guest_name=row[2],
                phone=row[3],
                email=row[4],
                check_in_date=row[5],
                check_out_date=row[6],
                num_guests=row[7],
                status=row[8],
                total_cost=row[9],
                created_at=row[10],
                updated_at=row[11]
            ))
        
        conn.close()
        return reservations
    else:
        # CSV backend
        rs = list_reservations(reservations_path)
        # Include reservations that overlap the date range
        # Overlap condition: check_in <= end_date AND check_out >= start_date
        filtered = [r for r in rs if r.check_in_date <= end_date and r.check_out_date >= start_date]
        return sorted(filtered, key=lambda x: x.check_in_date)
