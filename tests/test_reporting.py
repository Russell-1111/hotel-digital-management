from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import tempfile

from app.reporting import daily_checkin_list, daily_checkout_list, monthly_revenue_summary, guest_reservation_detail_report, compute_nights
from app.reservations import Reservation
from app.rooms import AppConfig
from app import storage_sqlite

def seed_reservations(tmp_path: Path):
    """Seed test reservations into SQLite database."""
    # Create test config
    cfg = AppConfig(
        data_dir=tmp_path,
        backup_dir=tmp_path / 'backups',
        use_sqlite=True,
        check_in_time='14:00',
        check_out_time='11:00',
        backup_time='02:30',
        backup_retention_days=7,
        service_charge_rate=0.10,
        tax_rate=0.06,
        currency='MYR',
        timezone='UTC',
        remember_username=False,
        last_username=''
    )
    
    # Initialize database
    db_path = storage_sqlite.ensure_db(cfg)
    
    # Seed rooms first (foreign key requirement)
    with storage_sqlite.get_connection(db_path) as conn:
        rooms = [
            ('101', 'Standard', 100.0, ''),
            ('102', 'Standard', 100.0, ''),
            ('103', 'Deluxe', 150.0, '')
        ]
        for room in rooms:
            conn.execute("""
                INSERT INTO rooms (room_id, room_type, base_price, image_path)
                VALUES (?, ?, ?, ?)
            """, room)
    
    # Seed test data
    reservations = [
        {
            'id': 'r1', 'room_id': '101', 'guest_name': 'A', 'guest_phone': '1234',
            'guest_email': 'a@gmail.com', 'start_date': '2025-10-24', 'end_date': '2025-10-25',
            'num_guests': 2, 'status': 'Confirmed', 'total_cost': 100.00,
            'created_at': '2025-10-23T10:00:00+00:00', 'updated_at': '2025-10-23T10:00:00+00:00'
        },
        {
            'id': 'r2', 'room_id': '102', 'guest_name': 'B', 'guest_phone': '1234',
            'guest_email': 'b@gmail.com', 'start_date': '2025-10-23', 'end_date': '2025-10-24',
            'num_guests': 2, 'status': 'Checked-In', 'total_cost': 200.00,
            'created_at': '2025-10-22T10:00:00+00:00', 'updated_at': '2025-10-23T14:05:00+00:00'
        },
        {
            'id': 'r3', 'room_id': '103', 'guest_name': 'C', 'guest_phone': '1234',
            'guest_email': 'c@gmail.com', 'start_date': '2025-09-30', 'end_date': '2025-10-01',
            'num_guests': 1, 'status': 'Checked-Out', 'total_cost': 150.00,
            'created_at': '2025-09-28T10:00:00+00:00', 'updated_at': '2025-10-01T11:10:00+00:00'
        }
    ]
    
    with storage_sqlite.get_connection(db_path) as conn:
        for res in reservations:
            conn.execute("""
                INSERT INTO reservations (
                    id, room_id, guest_name, guest_phone, guest_email,
                    start_date, end_date, num_guests, status,
                    total_cost, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                res['id'], res['room_id'], res['guest_name'], res['guest_phone'],
                res['guest_email'], res['start_date'], res['end_date'], res['num_guests'],
                res['status'], res['total_cost'], res['created_at'], res['updated_at']
            ))
    
    return db_path


def test_daily_lists(tmp_path: Path):
    path = seed_reservations(tmp_path)
    hotel_tz = ZoneInfo("Asia/Kuala_Lumpur")
    ins = daily_checkin_list(path, "2025-10-24", hotel_tz)
    outs = daily_checkout_list(path, "2025-10-24", hotel_tz)
    assert [r.reservation_id for r in ins] == ["r1"]
    assert [r.reservation_id for r in outs] == ["r2"]


def test_monthly_revenue(tmp_path: Path):
    path = seed_reservations(tmp_path)
    total = monthly_revenue_summary(path, "2025-10")
    # r1, r2, r3 all check_out in October 2025 => 100 + 200 + 150
    assert total == 450.00


def test_compute_nights():
    nights = compute_nights("2025-10-24", "2025-10-27")
    assert nights == 3
    
    same_day = compute_nights("2025-10-24", "2025-10-24")
    assert same_day == 0


def test_guest_reservation_detail_report(tmp_path: Path):
    path = seed_reservations(tmp_path)
    
    # Test normal case - filter by October 2025 (overlapping reservations)
    results = guest_reservation_detail_report(path, "2025-10-01", "2025-10-31")
    assert len(results) == 3  # r1, r2, and r3 all overlap with October range
    
    # Test exact date range match
    exact = guest_reservation_detail_report(path, "2025-10-24", "2025-10-25")
    assert len(exact) == 2  # r1 and r2 overlap with this range
    
    # Test empty results - no reservations in this range
    empty = guest_reservation_detail_report(path, "2025-11-01", "2025-11-30")
    assert len(empty) == 0
    
    # Test multiple rooms - verify all fields present
    results = guest_reservation_detail_report(path, "2025-09-01", "2025-10-31")
    assert len(results) == 3  # All three reservations
    for res in results:
        assert res.guest_name
        assert res.room_id
        assert res.check_in_date
        assert res.check_out_date
        assert res.total_cost > 0
