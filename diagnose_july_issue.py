import sqlite3
from pathlib import Path

db_path = Path("data/reservations.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== DIAGNOSING JULY 1ST ISSUE ===\n")

# Check for July 1st check-ins
cursor.execute("""
    SELECT COUNT(*), GROUP_CONCAT(status)
    FROM reservations 
    WHERE start_date = '2025-07-01'
""")
result = cursor.fetchone()
print(f"Check-ins on July 1st: {result[0]} reservations")
if result[0] > 0:
    print(f"  Statuses: {result[1]}")

# Check for July 1st check-outs
cursor.execute("""
    SELECT COUNT(*), GROUP_CONCAT(status)
    FROM reservations 
    WHERE end_date = '2025-07-01'
""")
result = cursor.fetchone()
print(f"Check-outs on July 1st: {result[0]} reservations")
if result[0] > 0:
    print(f"  Statuses: {result[1]}")

# Sample July 1st data
cursor.execute("""
    SELECT guest_name, room_id, start_date, end_date, status
    FROM reservations 
    WHERE start_date = '2025-07-01' OR end_date = '2025-07-01'
    ORDER BY start_date, end_date
    LIMIT 10
""")

print(f"\nSample July 1st reservations:")
for row in cursor.fetchall():
    print(f"  Room {row[1]}: {row[0]} | {row[2]} -> {row[3]} | {row[4]}")

# Check room availability for July 1-2
print(f"\n=== CHECKING ROOM AVAILABILITY (July 1-2) ===")
cursor.execute("""
    SELECT room_id, COUNT(*) as bookings
    FROM reservations
    WHERE status NOT IN ('Cancelled')
      AND start_date < '2025-07-02' 
      AND end_date > '2025-07-01'
    GROUP BY room_id
    ORDER BY room_id
""")

occupied_rooms = {row[0]: row[1] for row in cursor.fetchall()}
print(f"Occupied rooms for July 1-2: {list(occupied_rooms.keys())}")

all_rooms = ['101', '102', '103', '104']
available_rooms = [r for r in all_rooms if r not in occupied_rooms]
print(f"Available rooms for July 1-2: {available_rooms}")

if len(available_rooms) == 4:
    print("\n⚠ WARNING: All rooms show as available - data might not be loaded correctly!")

conn.close()
