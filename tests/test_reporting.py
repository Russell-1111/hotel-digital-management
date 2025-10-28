from pathlib import Path
from datetime import datetime

from app.reporting import daily_checkin_list, daily_checkout_list, monthly_revenue_summary, guest_reservation_detail_report, compute_nights
from app.reservations import Reservation
from app.storage import write_csv_atomic

FIELDNAMES = [
    "reservation_id","room_id","guest_name","phone","email",
    "check_in_date","check_out_date","num_guests","status","total_cost","created_at","updated_at"
]

def seed_reservations(tmp_path: Path):
    path = tmp_path / 'reservations.csv'
    rows = [
        {
            "reservation_id": "r1","room_id": "101","guest_name": "A","phone": "","email": "",
            "check_in_date": "2025-10-24","check_out_date": "2025-10-25","num_guests": "2","status": "Confirmed","total_cost": "100.00","created_at": "2025-10-23T10:00:00","updated_at": "2025-10-23T10:00:00"
        },
        {
            "reservation_id": "r2","room_id": "102","guest_name": "B","phone": "","email": "",
            "check_in_date": "2025-10-23","check_out_date": "2025-10-24","num_guests": "2","status": "Checked-In","total_cost": "200.00","created_at": "2025-10-22T10:00:00","updated_at": "2025-10-23T14:05:00"
        },
        {
            "reservation_id": "r3","room_id": "103","guest_name": "C","phone": "","email": "",
            "check_in_date": "2025-09-30","check_out_date": "2025-10-01","num_guests": "1","status": "Checked-Out","total_cost": "150.00","created_at": "2025-09-28T10:00:00","updated_at": "2025-10-01T11:10:00"
        }
    ]
    write_csv_atomic(path, FIELDNAMES, rows)
    return path


def test_daily_lists(tmp_path: Path):
    path = seed_reservations(tmp_path)
    ins = daily_checkin_list(path, "2025-10-24")
    outs = daily_checkout_list(path, "2025-10-24")
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
    
    # Test normal case - filter by October 2025
    results = guest_reservation_detail_report(path, "2025-10-01", "2025-10-31")
    assert len(results) == 2  # r1 and r2 have check-in in October
    assert results[0].reservation_id == "r2"  # Sorted by check_in_date: Oct 23 comes first
    assert results[1].reservation_id == "r1"  # Oct 24 comes second
    
    # Test edge case - exact date match
    exact = guest_reservation_detail_report(path, "2025-10-24", "2025-10-24")
    assert len(exact) == 1
    assert exact[0].reservation_id == "r1"
    
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
