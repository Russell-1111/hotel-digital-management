"""
Test script to verify the fix for guest reservation details reporting.
"""

from pathlib import Path
from app.reporting import guest_reservation_detail_report

# Test the fixed function
reservations_path = Path("data/reservations.db")
start_date = "2025-09-01"
end_date = "2025-11-30"

print("=== TESTING FIXED GUEST RESERVATION DETAIL REPORT ===\n")
print(f"Date Range: {start_date} to {end_date}")
print()

reservations = guest_reservation_detail_report(reservations_path, start_date, end_date)

print(f"✓ Total Reservations Found: {len(reservations)}")
print()

# Show first 10 reservations
print("First 10 reservations:")
print(f"{'Guest Name':<20} {'Check-In':<12} {'Check-Out':<12} {'Status':<15} {'Total (MYR)':<12}")
print("=" * 85)

for i, res in enumerate(reservations[:10]):
    print(f"{res.guest_name:<20} {res.check_in_date:<12} {res.check_out_date:<12} {res.status:<15} {res.total_cost:>11.2f}")

if len(reservations) > 10:
    print(f"... and {len(reservations) - 10} more")

print()

# Calculate total revenue
total_revenue = sum(r.total_cost for r in reservations if r.status in ['Checked-Out', 'Checked-In'])
print(f"Total Revenue (Checked-Out + Checked-In): MYR {total_revenue:,.2f}")

# Status breakdown
status_counts = {}
for res in reservations:
    status_counts[res.status] = status_counts.get(res.status, 0) + 1

print(f"\nStatus Breakdown:")
for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count}")

print("\n=== TEST RESULT ===")
if len(reservations) == 259:
    print("✅ PASS: Found expected 259 reservations (including 7 that checked in before Sept 1)")
else:
    print(f"⚠ WARNING: Found {len(reservations)} reservations (expected 259)")
    if len(reservations) == 252:
        print("❌ FAIL: Still missing 7 reservations that checked in before Sept 1")
    
print("\nThe fix ensures all reservations overlapping the period are included,")
print("not just those with check-in dates within the range.")
