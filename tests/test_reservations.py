from pathlib import Path
from datetime import datetime, timedelta
from app.reservations import (
    create_reservation,
    cancel_reservation,
    modify_reservation,
    list_reservations,
    is_room_available,
    auto_status_transitions,
)
from app.rooms import Room
from app.config import AppConfig
from app.storage import write_csv_atomic

FIELDNAMES = [
    "reservation_id","room_id","guest_name","phone","email",
    "check_in_date","check_out_date","num_guests","status","total_cost","created_at","updated_at"
]


def test_create_reservation(tmp_path: Path):
    """Test creating a new reservation."""
    reservations_path = tmp_path / "reservations.csv"
    reservations_path.write_text("reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at\n", encoding='utf-8')
    
    cfg = AppConfig(
        data_dir=tmp_path, backup_dir=tmp_path, check_in_time="14:00", check_out_time="11:00",
        backup_time="02:30", backup_retention_days=7, service_charge_rate=0.10, tax_rate=0.06, currency="MYR"
    )
    
    room = Room(room_id="101", room_type="Standard", base_price=100.0)
    
    res = create_reservation(
        cfg, reservations_path, room,
        "John Doe", "123456", "john@example.com",
        "2025-10-25", "2025-10-27", 2
    )
    
    assert res.room_id == "101"
    assert res.guest_name == "John Doe"
    assert res.status == "Confirmed"
    assert res.total_cost == 233.2  # 2 nights @ 100: subtotal 200 + 20 service + 13.2 tax
    
    # Verify persisted
    reservations = list_reservations(reservations_path)
    assert len(reservations) == 1
    assert reservations[0].guest_name == "John Doe"


def test_prevent_double_booking(tmp_path: Path):
    """Test that overlapping reservations are rejected."""
    reservations_path = tmp_path / "reservations.csv"
    reservations_path.write_text("reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at\n", encoding='utf-8')
    
    cfg = AppConfig(
        data_dir=tmp_path, backup_dir=tmp_path, check_in_time="14:00", check_out_time="11:00",
        backup_time="02:30", backup_retention_days=7, service_charge_rate=0.10, tax_rate=0.06, currency="MYR"
    )
    
    room = Room(room_id="101", room_type="Standard", base_price=100.0)
    
    # First reservation
    create_reservation(cfg, reservations_path, room, "Alice", "111", "a@x.com", "2025-10-25", "2025-10-27", 2)
    
    # Try overlapping reservation
    try:
        create_reservation(cfg, reservations_path, room, "Bob", "222", "b@x.com", "2025-10-26", "2025-10-28", 1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not available" in str(e)


def test_cancel_reservation(tmp_path: Path):
    """Test cancelling a reservation frees the room."""
    reservations_path = tmp_path / "reservations.csv"
    reservations_path.write_text("reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at\n", encoding='utf-8')
    
    cfg = AppConfig(
        data_dir=tmp_path, backup_dir=tmp_path, check_in_time="14:00", check_out_time="11:00",
        backup_time="02:30", backup_retention_days=7, service_charge_rate=0.10, tax_rate=0.06, currency="MYR"
    )
    
    room = Room(room_id="101", room_type="Standard", base_price=100.0)
    
    res = create_reservation(cfg, reservations_path, room, "Alice", "111", "a@x.com", "2025-10-25", "2025-10-27", 2)
    
    # Cancel
    success = cancel_reservation(reservations_path, res.reservation_id)
    assert success
    
    # Verify status
    reservations = list_reservations(reservations_path)
    assert reservations[0].status == "Cancelled"
    
    # Should now be available for booking
    assert is_room_available(reservations, "101", "2025-10-25", "2025-10-27")


def test_modify_reservation_dates(tmp_path: Path):
    """Test modifying reservation dates with availability recheck."""
    reservations_path = tmp_path / "reservations.csv"
    reservations_path.write_text("reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at\n", encoding='utf-8')
    
    # Create rooms.csv for modify to find base price
    rooms_path = tmp_path / "rooms.csv"
    rooms_path.write_text("room_id,room_type,base_price\n101,Standard,100.00\n102,Deluxe,150.00\n", encoding='utf-8')
    
    cfg = AppConfig(
        data_dir=tmp_path, backup_dir=tmp_path, check_in_time="14:00", check_out_time="11:00",
        backup_time="02:30", backup_retention_days=7, service_charge_rate=0.10, tax_rate=0.06, currency="MYR"
    )
    
    room = Room(room_id="101", room_type="Standard", base_price=100.0)
    
    res = create_reservation(cfg, reservations_path, room, "Alice", "111", "a@x.com", "2025-10-25", "2025-10-27", 2)
    original_cost = res.total_cost
    
    # Modify to extend stay by 1 night
    success = modify_reservation(cfg, reservations_path, res.reservation_id, new_check_out="2025-10-28")
    assert success
    
    # Verify changes
    reservations = list_reservations(reservations_path)
    assert reservations[0].check_out_date == "2025-10-28"
    # 3 nights @ 100: subtotal 300 + 30 service + 19.8 tax = 349.8
    assert reservations[0].total_cost == 349.8


def test_modify_reservation_guest_info(tmp_path: Path):
    """Test modifying guest information without changing dates."""
    reservations_path = tmp_path / "reservations.csv"
    reservations_path.write_text("reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at\n", encoding='utf-8')
    
    rooms_path = tmp_path / "rooms.csv"
    rooms_path.write_text("room_id,room_type,base_price\n101,Standard,100.00\n", encoding='utf-8')
    
    cfg = AppConfig(
        data_dir=tmp_path, backup_dir=tmp_path, check_in_time="14:00", check_out_time="11:00",
        backup_time="02:30", backup_retention_days=7, service_charge_rate=0.10, tax_rate=0.06, currency="MYR"
    )
    
    room = Room(room_id="101", room_type="Standard", base_price=100.0)
    
    res = create_reservation(cfg, reservations_path, room, "Alice", "111", "a@x.com", "2025-10-25", "2025-10-27", 2)
    original_cost = res.total_cost
    
    # Modify guest info only
    success = modify_reservation(
        cfg, reservations_path, res.reservation_id,
        new_guest_name="Alice Smith",
        new_phone="999",
        new_email="alice.smith@example.com"
    )
    assert success
    
    # Verify changes
    reservations = list_reservations(reservations_path)
    assert reservations[0].guest_name == "Alice Smith"
    assert reservations[0].phone == "999"
    assert reservations[0].email == "alice.smith@example.com"
    assert reservations[0].total_cost == original_cost  # Cost unchanged


def test_auto_status_transitions(tmp_path: Path):
    """Test automatic status transitions at check-in and check-out times."""
    reservations_path = tmp_path / "reservations.csv"
    
    # Create a reservation that should transition to Checked-In
    now = datetime.now()
    checkin_date = now.strftime('%Y-%m-%d')
    checkout_date = (now + timedelta(days=2)).strftime('%Y-%m-%d')
    
    rows = [{
        "reservation_id": "r1",
        "room_id": "101",
        "guest_name": "Alice",
        "phone": "111",
        "email": "a@x.com",
        "check_in_date": checkin_date,
        "check_out_date": checkout_date,
        "num_guests": "2",
        "status": "Confirmed",
        "total_cost": "233.20",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }]
    
    write_csv_atomic(reservations_path, FIELDNAMES, rows)
    
    # Simulate time at 14:05 (after check-in time)
    simulated_time = now.replace(hour=14, minute=5, second=0, microsecond=0)
    auto_status_transitions(reservations_path, simulated_time, "14:00", "11:00")
    
    # Should now be Checked-In
    reservations = list_reservations(reservations_path)
    assert reservations[0].status == "Checked-In"
    
    # Now simulate checkout time
    checkout_time = datetime.strptime(checkout_date, '%Y-%m-%d').replace(hour=11, minute=5)
    auto_status_transitions(reservations_path, checkout_time, "14:00", "11:00")
    
    reservations = list_reservations(reservations_path)
    assert reservations[0].status == "Checked-Out"


def test_is_room_available_logic(tmp_path: Path):
    """Test room availability checking with various scenarios."""
    reservations_path = tmp_path / "reservations.csv"
    
    rows = [
        {
            "reservation_id": "r1", "room_id": "101", "guest_name": "Alice", "phone": "", "email": "",
            "check_in_date": "2025-10-25", "check_out_date": "2025-10-27", "num_guests": "2",
            "status": "Confirmed", "total_cost": "200.00", "created_at": "", "updated_at": ""
        },
        {
            "reservation_id": "r2", "room_id": "102", "guest_name": "Bob", "phone": "", "email": "",
            "check_in_date": "2025-10-26", "check_out_date": "2025-10-28", "num_guests": "1",
            "status": "Cancelled", "total_cost": "150.00", "created_at": "", "updated_at": ""
        }
    ]
    
    write_csv_atomic(reservations_path, FIELDNAMES, rows)
    reservations = list_reservations(reservations_path)
    
    # Room 101 occupied during 25-27
    assert not is_room_available(reservations, "101", "2025-10-25", "2025-10-27")
    assert not is_room_available(reservations, "101", "2025-10-26", "2025-10-28")
    
    # Room 101 available before and after
    assert is_room_available(reservations, "101", "2025-10-23", "2025-10-25")
    assert is_room_available(reservations, "101", "2025-10-27", "2025-10-29")
    
    # Room 102 available (cancelled reservation)
    assert is_room_available(reservations, "102", "2025-10-26", "2025-10-28")
    
    # Room 103 available (no reservations)
    assert is_room_available(reservations, "103", "2025-10-25", "2025-10-27")
