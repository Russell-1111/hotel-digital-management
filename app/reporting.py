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
        reservations_path: Path to reservations file
        date_str: Date in YYYY-MM-DD format (interpreted as midnight in hotel timezone)
        hotel_tz: ZoneInfo object for hotel timezone
        
    Returns:
        List of Reservation objects with check-in on the specified date
    """
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
        reservations_path: Path to reservations file
        date_str: Date in YYYY-MM-DD format (interpreted as midnight in hotel timezone)
        hotel_tz: ZoneInfo object for hotel timezone
        
    Returns:
        List of Reservation objects with check-out on the specified date
    """
    rs = list_reservations(reservations_path)
    valid = []
    for r in rs:
        # Skip invalid reservations (check-in must be before check-out)
        if r.check_in_date >= r.check_out_date:
            continue
        if r.check_out_date == date_str and r.status in {"Checked-In"}:
            valid.append(r)
    return valid


def monthly_revenue_summary(reservations_path: Path, year_month: str) -> float:
    # year_month format: YYYY-MM
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
    Filters by check_in_date >= start_date AND check_in_date <= end_date.
    Returns list sorted by check_in_date ascending.
    """
    rs = list_reservations(reservations_path)
    filtered = [r for r in rs if start_date <= r.check_in_date <= end_date]
    return sorted(filtered, key=lambda x: x.check_in_date)
