"""
Test the fixed monthly_revenue_summary function.
"""

from pathlib import Path
from app.reporting import monthly_revenue_summary

db_path = Path("data/reservations.db")

print("=== TESTING FIXED MONTHLY REVENUE SUMMARY ===\n")

# Test June 2025
june_revenue = monthly_revenue_summary(db_path, "2025-06")
print(f"June 2025 Revenue: MYR {june_revenue:.2f}")

# Test all months from June to November
months = ["2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11"]

print("\n=== MONTHLY REVENUE SUMMARY (June - November 2025) ===")
print(f"{'Month':<12} {'Revenue (MYR)':<15}")
print("=" * 30)

total = 0.0
for month in months:
    revenue = monthly_revenue_summary(db_path, month)
    total += revenue
    print(f"{month:<12} {revenue:>12.2f}")

print("=" * 30)
print(f"{'TOTAL':<12} {total:>12.2f}")

print("\n=== VERIFICATION ===")
import sqlite3
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get actual total from database
cursor.execute("""
    SELECT SUM(total_cost)
    FROM reservations
    WHERE end_date >= '2025-06-01' AND end_date <= '2025-11-30'
""")
db_total = cursor.fetchone()[0] or 0

conn.close()

print(f"Database total (June-Nov check-outs): MYR {db_total:.2f}")
print(f"Function total (sum of monthly):       MYR {total:.2f}")

if abs(db_total - total) < 0.01:
    print("\n✅ PASS: Monthly revenue summary is now working correctly!")
    print(f"✓ June 2025 now shows MYR {june_revenue:.2f} (was MYR 0.00)")
else:
    print(f"\n⚠ Difference: MYR {abs(db_total - total):.2f}")
