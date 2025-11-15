"""Test booking a room for July 1-2, 2025 to see what happens"""
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

# Check availability for July 1-2
db_path = cfg.data_dir / 'reservations.db'
reservations = list_reservations(db_path, cfg)

print("=" * 60)
print("TESTING JULY 1-2, 2025 BOOKING")
print("=" * 60)

start_date = '2025-07-01'
end_date = '2025-07-02'

# Check availability
available = is_room_available(reservations, '101', start_date, end_date)
print(f"\nRoom 101 available for {start_date} to {end_date}: {available}")

# Show existing reservations for Room 101
print(f"\nExisting reservations for Room 101 around this date:")
for r in reservations:
    if r.room_id == '101':
        # Check if it overlaps
        r_start = datetime.strptime(r.check_in_date, '%Y-%m-%d')
        r_end = datetime.strptime(r.check_out_date, '%Y-%m-%d')
        req_start = datetime.strptime(start_date, '%Y-%m-%d')
        req_end = datetime.strptime(end_date, '%Y-%m-%d')
        
        overlaps = max(req_start, r_start) < min(req_end, r_end)
        
        if overlaps:
            print(f"  {r.check_in_date} to {r.check_out_date} - {r.status} - {r.guest_name}")
            print(f"    → Overlaps: YES, Counted in availability: {'NO (excluded)' if r.status in ['Cancelled', 'Checked-Out'] else 'YES (blocks room)'}")

if available:
    print(f"\n✓ Room 101 IS available - can proceed with booking")
else:
    print(f"\n✗ Room 101 NOT available - booking should fail")

print("\n" + "=" * 60)
