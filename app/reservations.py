from __future__ import annotations
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from .rooms import AppConfig
from .rooms import Room
from .storage import read_csv, write_csv_atomic, file_lock


def validate_phone(phone: str) -> None:
    """
    Validate phone number contains only digits.
    
    Args:
        phone: Phone number string to validate
        
    Raises:
        ValueError: If phone contains non-digit characters
    """
    if not phone.strip():
        raise ValueError("Phone number is required")
    
    if not phone.strip().isdigit():
        raise ValueError("Please enter a valid phone number containing only digits")


def validate_email(email: str) -> None:
    """
    Validate email address ends with @gmail.com or @outlook.com.
    
    Args:
        email: Email address string to validate
        
    Raises:
        ValueError: If email doesn't end with @gmail.com or @outlook.com
    """
    if not email.strip():
        raise ValueError("Email address is required")
    
    email_lower = email.strip().lower()
    
    # Check if email ends with allowed domains
    if not (email_lower.endswith('@gmail.com') or email_lower.endswith('@outlook.com')):
        raise ValueError("Email must end with @gmail.com or @outlook.com")
    
    # Check if there's a username before the @ symbol
    if email_lower.startswith('@'):
        raise ValueError("Email must end with @gmail.com or @outlook.com")


def validate_guest_info(guest_name: str, phone: str, email: str) -> None:
    """
    Validate all required guest information fields.
    
    Args:
        guest_name: Guest name string
        phone: Phone number string
        email: Email address string
        
    Raises:
        ValueError: If any field is empty or invalid
    """
    if not guest_name.strip():
        raise ValueError("Guest name is required")
    
    validate_phone(phone)
    validate_email(email)


def compute_total(nightly_rate: float, nights: int, service_rate: float, tax_rate: float) -> float:
    """
    Calculate total stay cost with service charge and tax.
    
    Formula:
    - subtotal = nightly_rate × nights
    - service = subtotal × service_rate (10%)
    - tax_base = subtotal + service
    - tax = tax_base × tax_rate (6%)
    - total = subtotal + service + tax
    """
    if nights <= 0:
        return 0.0
    subtotal = nightly_rate * nights
    service = round(subtotal * service_rate, 2)
    tax_base = subtotal + service
    tax = round(tax_base * tax_rate, 2)
    total = round(subtotal + service + tax, 2)
    return total


@dataclass
class Reservation:
    reservation_id: str
    room_id: str
    guest_name: str
    phone: str
    email: str
    check_in_date: str  # YYYY-MM-DD
    check_out_date: str  # YYYY-MM-DD
    num_guests: int
    status: str  # Confirmed | Cancelled | Checked-In | Checked-Out
    total_cost: float
    created_at: str
    updated_at: str


FIELDNAMES = [
    "reservation_id","room_id","guest_name","phone","email",
    "check_in_date","check_out_date","num_guests","status","total_cost","created_at","updated_at"
]


def _parse_date(d: str) -> datetime:
    return datetime.strptime(d, "%Y-%m-%d")


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)


def list_reservations(path: Path) -> List[Reservation]:
    rows = read_csv(path)
    res: List[Reservation] = []
    for r in rows:
        res.append(Reservation(
            reservation_id=r["reservation_id"],
            room_id=r["room_id"],
            guest_name=r["guest_name"],
            phone=r["phone"],
            email=r["email"],
            check_in_date=r["check_in_date"],
            check_out_date=r["check_out_date"],
            num_guests=int(r["num_guests"] or 0),
            status=r["status"],
            total_cost=float(r["total_cost"] or 0),
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        ))
    return res


def is_room_available(reservations: List[Reservation], room_id: str, start_date: str, end_date: str) -> bool:
    start = _parse_date(start_date)
    end = _parse_date(end_date)
    for r in reservations:
        if r.room_id != room_id:
            continue
        if r.status in {"Cancelled", "Checked-Out"}:
            continue
        r_start = _parse_date(r.check_in_date)
        r_end = _parse_date(r.check_out_date)
        if _overlaps(start, end, r_start, r_end):
            return False
    return True


def _nights(check_in_date: str, check_out_date: str) -> int:
    return (_parse_date(check_out_date) - _parse_date(check_in_date)).days


def create_reservation(cfg: AppConfig, reservations_path: Path, room: Room, guest_name: str, phone: str, email: str, check_in_date: str, check_out_date: str, num_guests: int) -> Reservation:
    # Validate guest information (name, phone, email)
    validate_guest_info(guest_name, phone, email)
    
    # Validate check-in date is not in the past
    today = datetime.now().date()
    checkin_date = _parse_date(check_in_date).date()
    if checkin_date < today:
        raise ValueError("Check-in date cannot be in the past")
    
    # Validate check-in is before check-out
    if _parse_date(check_in_date) >= _parse_date(check_out_date):
        raise ValueError("Check-in date must be before check-out date")
    
    # Read existing
    existing = list_reservations(reservations_path)
    if not is_room_available(existing, room.room_id, check_in_date, check_out_date):
        raise ValueError("Room not available for the selected dates")

    rid = str(uuid.uuid4())
    nights = _nights(check_in_date, check_out_date)
    total = compute_total(room.base_price, nights, cfg.service_charge_rate, cfg.tax_rate)
    now = datetime.now().isoformat(timespec='seconds')
    new = Reservation(
        reservation_id=rid,
        room_id=room.room_id,
        guest_name=guest_name,
        phone=phone,
        email=email,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        num_guests=num_guests,
        status="Confirmed",
        total_cost=total,
        created_at=now,
        updated_at=now,
    )

    # Persist with atomic write
    rows: List[Dict[str, str]] = []
    for r in existing + [new]:
        rows.append({
            "reservation_id": r.reservation_id,
            "room_id": r.room_id,
            "guest_name": r.guest_name,
            "phone": r.phone,
            "email": r.email,
            "check_in_date": r.check_in_date,
            "check_out_date": r.check_out_date,
            "num_guests": str(r.num_guests),
            "status": r.status,
            "total_cost": f"{r.total_cost:.2f}",
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        })
    write_csv_atomic(reservations_path, FIELDNAMES, rows)
    return new


def modify_reservation(
    cfg: AppConfig,
    reservations_path: Path,
    reservation_id: str,
    new_room: Optional[Room] = None,
    new_check_in: Optional[str] = None,
    new_check_out: Optional[str] = None,
    new_num_guests: Optional[int] = None,
    new_guest_name: Optional[str] = None,
    new_phone: Optional[str] = None,
    new_email: Optional[str] = None,
) -> bool:
    """Modify an existing reservation. Re-validates availability if room or dates change."""
    existing = list_reservations(reservations_path)
    target = None
    for r in existing:
        if r.reservation_id == reservation_id:
            target = r
            break
    if not target or target.status in {"Cancelled", "Checked-Out"}:
        return False

    # Validate guest information changes
    if new_guest_name is not None and not new_guest_name.strip():
        raise ValueError("Guest name is required")
    if new_phone is not None:
        validate_phone(new_phone)
    if new_email is not None:
        validate_email(new_email)

    # Apply changes
    if new_guest_name is not None:
        target.guest_name = new_guest_name
    if new_phone is not None:
        target.phone = new_phone
    if new_email is not None:
        target.email = new_email
    if new_num_guests is not None:
        target.num_guests = new_num_guests

    room_changed = new_room is not None
    dates_changed = new_check_in is not None or new_check_out is not None

    final_room_id = new_room.room_id if new_room else target.room_id
    final_check_in = new_check_in if new_check_in else target.check_in_date
    final_check_out = new_check_out if new_check_out else target.check_out_date

    # Validate check-in date is not in the past (only if dates are being changed)
    if dates_changed:
        today = datetime.now().date()
        checkin_date = _parse_date(final_check_in).date()
        if checkin_date < today:
            raise ValueError("Check-in date cannot be in the past")

    # Validate check-in is before check-out
    if _parse_date(final_check_in) >= _parse_date(final_check_out):
        raise ValueError("Check-in date must be before check-out date")

    # If room or dates changed, re-check availability (excluding this reservation)
    if room_changed or dates_changed:
        others = [r for r in existing if r.reservation_id != reservation_id]
        if not is_room_available(others, final_room_id, final_check_in, final_check_out):
            raise ValueError("Room not available for the new dates")

    # Update fields
    if new_room:
        target.room_id = new_room.room_id
    if new_check_in:
        target.check_in_date = new_check_in
    if new_check_out:
        target.check_out_date = new_check_out

    # Recalculate total if room or dates changed
    if room_changed or dates_changed:
        nights = _nights(target.check_in_date, target.check_out_date)
        # Find the room's base price
        from .rooms import load_rooms
        from pathlib import Path as P
        rooms_path = reservations_path.parent / 'rooms.csv'
        rooms = load_rooms(rooms_path)
        room_obj = next((rm for rm in rooms if rm.room_id == target.room_id), None)
        if room_obj:
            target.total_cost = compute_total(room_obj.base_price, nights, cfg.service_charge_rate, cfg.tax_rate)

    target.updated_at = datetime.now().isoformat(timespec='seconds')

    # Write back
    rows: List[Dict[str, str]] = []
    for r in existing:
        rows.append({
            "reservation_id": r.reservation_id,
            "room_id": r.room_id,
            "guest_name": r.guest_name,
            "phone": r.phone,
            "email": r.email,
            "check_in_date": r.check_in_date,
            "check_out_date": r.check_out_date,
            "num_guests": str(r.num_guests),
            "status": r.status,
            "total_cost": f"{r.total_cost:.2f}",
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        })
    write_csv_atomic(reservations_path, FIELDNAMES, rows)
    return True


def cancel_reservation(reservations_path: Path, reservation_id: str) -> bool:
    existing = list_reservations(reservations_path)
    changed = False
    now = datetime.now().isoformat(timespec='seconds')
    for r in existing:
        if r.reservation_id == reservation_id and r.status not in {"Cancelled", "Checked-Out"}:
            r.status = "Cancelled"
            r.updated_at = now
            changed = True
            break
    if changed:
        rows: List[Dict[str, str]] = []
        for r in existing:
            rows.append({
                "reservation_id": r.reservation_id,
                "room_id": r.room_id,
                "guest_name": r.guest_name,
                "phone": r.phone,
                "email": r.email,
                "check_in_date": r.check_in_date,
                "check_out_date": r.check_out_date,
                "num_guests": str(r.num_guests),
                "status": r.status,
                "total_cost": f"{r.total_cost:.2f}",
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            })
        write_csv_atomic(reservations_path, FIELDNAMES, rows)
    return changed


def auto_status_transitions(reservations_path: Path, local_now: datetime, check_in_time: str, check_out_time: str) -> None:
    # Parse times
    in_hour, in_minute = map(int, check_in_time.split(':'))
    out_hour, out_minute = map(int, check_out_time.split(':'))

    existing = list_reservations(reservations_path)
    changed = False
    for r in existing:
        ci = _parse_date(r.check_in_date).replace(hour=in_hour, minute=in_minute, second=0, microsecond=0)
        co = _parse_date(r.check_out_date).replace(hour=out_hour, minute=out_minute, second=0, microsecond=0)
        if r.status == "Confirmed" and local_now >= ci:
            r.status = "Checked-In"
            r.updated_at = local_now.isoformat(timespec='seconds')
            changed = True
        if r.status == "Checked-In" and local_now >= co:
            r.status = "Checked-Out"
            r.updated_at = local_now.isoformat(timespec='seconds')
            changed = True
    if changed:
        rows: List[Dict[str, str]] = []
        for r in existing:
            rows.append({
                "reservation_id": r.reservation_id,
                "room_id": r.room_id,
                "guest_name": r.guest_name,
                "phone": r.phone,
                "email": r.email,
                "check_in_date": r.check_in_date,
                "check_out_date": r.check_out_date,
                "num_guests": str(r.num_guests),
                "status": r.status,
                "total_cost": f"{r.total_cost:.2f}",
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            })
        write_csv_atomic(reservations_path, FIELDNAMES, rows)
