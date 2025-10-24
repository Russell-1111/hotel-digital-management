from pathlib import Path
from datetime import datetime

from app.reporting import daily_checkin_list, daily_checkout_list, monthly_revenue_summary
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
