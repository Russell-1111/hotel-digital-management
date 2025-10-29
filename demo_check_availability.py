"""
Demo: How Check Availability Button Works
This script demonstrates the exact logic used by the "Check Availability" button
"""

from datetime import datetime
from pathlib import Path
from app.reservations import list_reservations, is_room_available
from app.rooms import load_rooms

# Load data
reservations_path = Path("data/reservations.csv")
rooms_path = Path("data/rooms.csv")

reservations = list_reservations(reservations_path)
rooms = load_rooms(rooms_path)

print("=" * 80)
print("CHECK AVAILABILITY BUTTON - HOW IT WORKS")
print("=" * 80)
print()

# Show current active reservations
print("STEP 1: Load all active reservations (excluding Cancelled and Checked-Out)")
print("-" * 80)
active_reservations = [r for r in reservations if r.status not in {"Cancelled", "Checked-Out"}]
for r in active_reservations:
    print(f"  Room {r.room_id}: {r.guest_name:20} | {r.check_in_date} -> {r.check_out_date} | Status: {r.status}")
print()

# Example scenarios
print("=" * 80)
print("REAL EXAMPLES - Check Availability Button Logic")
print("=" * 80)
print()

# Example 1: Checking availability for dates that overlap
print("EXAMPLE 1: Check availability for Room 101 from 2025-10-30 to 2025-10-31")
print("-" * 80)
check_in = "2025-10-30"
check_out = "2025-10-31"
room_id = "101"

print(f"User Input:")
print(f"  Check-in:  {check_in}")
print(f"  Check-out: {check_out}")
print()

print(f"Checking Room {room_id}...")
is_available = is_room_available(reservations, room_id, check_in, check_out)

# Show why it's not available
print(f"\nExisting reservations for Room {room_id}:")
for r in reservations:
    if r.room_id == room_id and r.status not in {"Cancelled", "Checked-Out"}:
        print(f"  ✗ {r.check_in_date} to {r.check_out_date} ({r.status}) - Guest: {r.guest_name}")
        
        # Check overlap
        r_start = datetime.strptime(r.check_in_date, "%Y-%m-%d")
        r_end = datetime.strptime(r.check_out_date, "%Y-%m-%d")
        req_start = datetime.strptime(check_in, "%Y-%m-%d")
        req_end = datetime.strptime(check_out, "%Y-%m-%d")
        
        if max(req_start, r_start) < min(req_end, r_end):
            print(f"    └─> OVERLAPS with your requested dates!")

print(f"\nResult: Room {room_id} is {'AVAILABLE ✓' if is_available else 'NOT AVAILABLE ✗'}")
print()

# Example 2: Checking availability for dates that don't overlap
print("=" * 80)
print("EXAMPLE 2: Check availability for Room 101 from 2025-11-01 to 2025-11-02")
print("-" * 80)
check_in = "2025-11-01"
check_out = "2025-11-02"
room_id = "101"

print(f"User Input:")
print(f"  Check-in:  {check_in}")
print(f"  Check-out: {check_out}")
print()

print(f"Checking Room {room_id}...")
is_available = is_room_available(reservations, room_id, check_in, check_out)

print(f"\nExisting active reservations for Room {room_id}:")
found_active = False
for r in reservations:
    if r.room_id == room_id and r.status not in {"Cancelled", "Checked-Out"}:
        print(f"  • {r.check_in_date} to {r.check_out_date} ({r.status})")
        found_active = True
        
        # Check overlap
        r_start = datetime.strptime(r.check_in_date, "%Y-%m-%d")
        r_end = datetime.strptime(r.check_out_date, "%Y-%m-%d")
        req_start = datetime.strptime(check_in, "%Y-%m-%d")
        req_end = datetime.strptime(check_out, "%Y-%m-%d")
        
        if max(req_start, r_start) < min(req_end, r_end):
            print(f"    └─> OVERLAPS with your requested dates!")
        else:
            print(f"    └─> No overlap - OK")

if not found_active:
    print(f"  (No active reservations)")

print(f"\nResult: Room {room_id} is {'AVAILABLE ✓' if is_available else 'NOT AVAILABLE ✗'}")
print()

# Example 3: Show all available rooms for a date range
print("=" * 80)
print("EXAMPLE 3: What 'Check Availability' button shows for 2025-11-01 to 2025-11-02")
print("-" * 80)
check_in = "2025-11-01"
check_out = "2025-11-02"

print(f"User Input:")
print(f"  Check-in:  {check_in}")
print(f"  Check-out: {check_out}")
print()

print("Checking all rooms...")
print("\nAvailable Rooms (what appears in dropdown):")
available_rooms = []
for room in rooms:
    if is_room_available(reservations, room.room_id, check_in, check_out):
        available_rooms.append(room)
        print(f"  ✓ {room.room_id} ({room.room_type}) - MYR {room.base_price:.2f}")

if not available_rooms:
    print("  (No rooms available)")
print()

# Example 4: Dates with same-day check-in and check-out
print("=" * 80)
print("EXAMPLE 4: Same-day booking (2025-11-05 to 2025-11-05)")
print("-" * 80)
check_in = "2025-11-05"
check_out = "2025-11-05"

print(f"User Input:")
print(f"  Check-in:  {check_in}")
print(f"  Check-out: {check_out}")
print()

print("Checking all rooms for same-day booking...")
print("\nAvailable Rooms:")
has_available = False
for room in rooms:
    if is_room_available(reservations, room.room_id, check_in, check_out):
        print(f"  ✓ {room.room_id} ({room.room_type}) - MYR {room.base_price:.2f}")
        has_available = True

if not has_available:
    print("  (No rooms available)")
print()

# Show the overlap detection algorithm
print("=" * 80)
print("HOW OVERLAP DETECTION WORKS")
print("=" * 80)
print()
print("The system uses this logic to detect date overlaps:")
print()
print("  def _overlaps(a_start, a_end, b_start, b_end):")
print("      return max(a_start, b_start) < min(a_end, b_end)")
print()
print("Examples:")
print("  • Reservation: 2025-10-28 to 2025-10-31")
print("  • Request:     2025-10-30 to 2025-10-31")
print("  • max(2025-10-30, 2025-10-28) = 2025-10-30")
print("  • min(2025-10-31, 2025-10-31) = 2025-10-31")
print("  • 2025-10-30 < 2025-10-31 = TRUE → OVERLAPS ✗")
print()
print("  • Reservation: 2025-10-28 to 2025-10-31")
print("  • Request:     2025-11-01 to 2025-11-02")
print("  • max(2025-11-01, 2025-10-28) = 2025-11-01")
print("  • min(2025-11-02, 2025-10-31) = 2025-10-31")
print("  • 2025-11-01 < 2025-10-31 = FALSE → NO OVERLAP ✓")
print()

print("=" * 80)
print("SUMMARY: Check Availability Button Flow")
print("=" * 80)
print()
print("1. User enters check-in and check-out dates")
print("2. User clicks 'Check Availability' button")
print("3. System validates date format (YYYY-MM-DD)")
print("4. System loads all existing reservations from CSV")
print("5. For each room in inventory:")
print("   - Check if room has any active reservations (not Cancelled/Checked-Out)")
print("   - Use overlap algorithm to detect conflicts")
print("   - If no conflicts, add to available list")
print("6. Populate dropdown with available rooms")
print("7. Auto-select first available room and show thumbnail")
print("8. If no rooms available, dropdown is empty")
print()
