import sqlite3
from pathlib import Path

db_path = Path("data/reservations.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check reservations with check-in date in Sept-Nov range
cursor.execute("""
    SELECT COUNT(*) 
    FROM reservations 
    WHERE start_date >= '2025-09-01' AND start_date <= '2025-11-30'
""")
checkin_count = cursor.fetchone()[0]

# Check reservations that overlap Sept-Nov period
cursor.execute("""
    SELECT COUNT(*) 
    FROM reservations 
    WHERE start_date <= '2025-11-30' AND end_date >= '2025-09-01'
""")
overlap_count = cursor.fetchone()[0]

# Show sample data
cursor.execute("""
    SELECT guest_name, start_date, end_date, status
    FROM reservations 
    WHERE start_date <= '2025-11-30' AND end_date >= '2025-09-01'
    ORDER BY start_date
    LIMIT 10
""")
samples = cursor.fetchall()

print("=== DIAGNOSIS ===")
print(f"Reservations with check-in in Sep-Nov: {checkin_count}")
print(f"Reservations overlapping Sep-Nov period: {overlap_count}")
print(f"\nSample overlapping reservations:")
for guest, start, end, status in samples:
    print(f"  {guest}: {start} -> {end} ({status})")

conn.close()
