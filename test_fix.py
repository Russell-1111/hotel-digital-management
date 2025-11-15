"""Test that the fix resolves the storage backend mismatch"""
import sys
from pathlib import Path
from datetime import datetime
from app.rooms import load_config, load_rooms
from app.reservations import list_reservations, is_room_available, create_reservation

# Load configuration
cfg = load_config(Path('config.ini'))

# Load rooms
rooms = load_rooms(cfg.data_dir / 'rooms.csv')
room_101 = next(r for r in rooms if r.room_id == '101')

# Use database path
db_path = cfg.data_dir / 'reservations.db'

print("=" * 70)
print("TESTING FIX: Storage Backend Consistency")
print("=" * 70)

# Test 1: Check availability
start_date = '2025-12-01'
end_date = '2025-12-02'

reservations_before = list_reservations(db_path, cfg)
print(f"\nBefore booking:")
print(f"  Total reservations in DB: {len(reservations_before)}")

available = is_room_available(reservations_before, '101', start_date, end_date)
print(f"  Room 101 available for {start_date} to {end_date}: {available}")

if not available:
    print("\n✗ Room 101 is not available - this doesn't match the screenshot")
    print("  Rooms should be available since all overlapping reservations are Checked-Out")
    sys.exit(1)

print(f"\n  ✓ Room 101 is available (correct)")

# Test 2: Try to create a reservation
print(f"\nAttempting to create reservation...")
try:
    new_res = create_reservation(
        cfg=cfg,
        reservations_path=db_path,
        room=room_101,
        guest_name="Test Guest",
        phone="1234567890",
        email="test@gmail.com",
        check_in_date=start_date,
        check_out_date=end_date,
        num_guests=2
    )
    print(f"  ✓ Reservation created successfully!")
    print(f"    Reservation ID: {new_res.reservation_id}")
    print(f"    Status: {new_res.status}")
    print(f"    Total Cost: MYR {new_res.total_cost:.2f}")
except Exception as e:
    print(f"  ✗ Failed to create reservation: {e}")
    sys.exit(1)

# Test 3: Verify it was written to the database
print(f"\nVerifying reservation was written to database...")
reservations_after = list_reservations(db_path, cfg)
print(f"  Total reservations after: {len(reservations_after)}")
print(f"  Difference: +{len(reservations_after) - len(reservations_before)}")

# Find the new reservation
found = any(r.reservation_id == new_res.reservation_id for r in reservations_after)
if found:
    print(f"  ✓ New reservation found in database!")
else:
    print(f"  ✗ New reservation NOT found in database - write failed!")
    sys.exit(1)

# Test 4: Verify room is now unavailable for the same dates
print(f"\nVerifying room is now unavailable...")
available_after = is_room_available(reservations_after, '101', start_date, end_date)
print(f"  Room 101 available after booking: {available_after}")

if available_after:
    print(f"  ✗ Room should NOT be available after booking!")
    sys.exit(1)
else:
    print(f"  ✓ Room correctly marked as unavailable!")

print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED - Fix is working correctly!")
print("=" * 70)
print("\nSummary:")
print("  1. ✓ Availability check reads from SQLite")
print("  2. ✓ Create reservation writes to SQLite")
print("  3. ✓ New reservation persisted in database")
print("  4. ✓ Availability check reflects new booking")
print("\nThe storage backend mismatch has been fixed!")
