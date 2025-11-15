import sqlite3
from pathlib import Path

db_path = Path("data/reservations.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== DIAGNOSING JUNE 2025 REVENUE ISSUE ===\n")

# Check reservations with June dates
cursor.execute("""
    SELECT COUNT(*), SUM(total_cost) 
    FROM reservations 
    WHERE start_date LIKE '2025-06%' OR end_date LIKE '2025-06%'
""")
result = cursor.fetchone()
print(f"Reservations overlapping June 2025: {result[0]} reservations, Total: MYR {result[1] or 0:.2f}")

# Check check-outs in June (what the monthly_revenue_summary uses)
cursor.execute("""
    SELECT COUNT(*), SUM(total_cost) 
    FROM reservations 
    WHERE end_date LIKE '2025-06%'
""")
result = cursor.fetchone()
print(f"Check-outs in June (all statuses): {result[0]} reservations, Total: MYR {result[1] or 0:.2f}")

# Check completed check-outs in June
cursor.execute("""
    SELECT COUNT(*), SUM(total_cost) 
    FROM reservations 
    WHERE end_date LIKE '2025-06%' AND status IN ('Checked-Out', 'Checked-In')
""")
result = cursor.fetchone()
print(f"Check-outs in June (Checked-Out/Checked-In): {result[0]} reservations, Total: MYR {result[1] or 0:.2f}")

# Sample of June reservations
cursor.execute("""
    SELECT guest_name, start_date, end_date, status, total_cost
    FROM reservations 
    WHERE end_date LIKE '2025-06%'
    ORDER BY end_date
    LIMIT 10
""")
print(f"\nSample June check-outs:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} -> {row[2]} ({row[3]}) MYR {row[4]:.2f}")

conn.close()

print("\n=== CHECKING monthly_revenue_summary FUNCTION ===")
from app.reporting import monthly_revenue_summary
from pathlib import Path

# Test with CSV path (will fail) and DB path
try:
    csv_path = Path("data/reservations.csv")
    result = monthly_revenue_summary(csv_path, "2025-06")
    print(f"Result from CSV path: MYR {result:.2f}")
except Exception as e:
    print(f"CSV path error: {e}")

# The function expects CSV but we're using SQLite
print("\n✗ ROOT CAUSE: monthly_revenue_summary() only works with CSV backend!")
print("  The function tries to read from CSV file, but system uses SQLite database.")
