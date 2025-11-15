import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('data/reservations.db')
conn.row_factory = sqlite3.Row

# Check what reservations exist for July 1-2
print("=" * 60)
print("RESERVATIONS OVERLAPPING JULY 1-2, 2025")
print("=" * 60)

cursor = conn.execute("""
    SELECT room_id, start_date, end_date, status, guest_name
    FROM reservations
    WHERE start_date < '2025-07-02' AND end_date > '2025-07-01'
    ORDER BY room_id, start_date
""")

reservations = cursor.fetchall()
if reservations:
    for r in reservations:
        print(f"Room {r['room_id']}: {r['start_date']} to {r['end_date']} ({r['status']}) - {r['guest_name']}")
else:
    print("No reservations found overlapping this period")

print()

# Check all rooms
cursor = conn.execute("SELECT room_id, room_type FROM rooms ORDER BY room_id")
rooms = cursor.fetchall()
print("=" * 60)
print("AVAILABILITY CHECK FOR JULY 1-2, 2025")
print("=" * 60)

for room in rooms:
    # Check availability using the same logic as storage_sqlite.py
    cursor = conn.execute("""
        SELECT COUNT(*) as count
        FROM reservations
        WHERE room_id = ?
          AND status NOT IN ('Cancelled', 'Checked-Out')
          AND start_date < ?
          AND end_date > ?
    """, (room['room_id'], '2025-07-02', '2025-07-01'))
    
    result = cursor.fetchone()
    is_available = result['count'] == 0
    
    status = "AVAILABLE ✓" if is_available else "NOT AVAILABLE ✗"
    print(f"Room {room['room_id']} ({room['room_type']}): {status} (conflicts: {result['count']})")

conn.close()
