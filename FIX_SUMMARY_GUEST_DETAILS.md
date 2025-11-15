# Root Cause Analysis & Fix Summary

## Problem Statement
The Guest Reservation Details report in the UI was not showing all reservations for the September-November 2025 period, while the analytics CSV file correctly showed all 259 reservations.

## Root Cause Identified

### Issue:
The `guest_reservation_detail_report()` function in `app/reporting.py` was filtering reservations using **check-in date only**:

```python
# OLD CODE (INCORRECT):
filtered = [r for r in rs if start_date <= r.check_in_date <= end_date]
```

This meant:
- ✅ Included: 252 reservations with check-in dates in Sept-Nov
- ❌ **Missing**: 7 reservations that checked in before Sept 1 but checked out during Sept-Nov
- **Total Missing**: 259 - 252 = **7 reservations**

### Example of Missing Reservations:
```
Daniel Young:        Check-in: 2025-08-29, Check-out: 2025-09-01 (overlaps Sept)
Christopher Hall:    Check-in: 2025-08-30, Check-out: 2025-09-01 (overlaps Sept)
Jessica King:        Check-in: 2025-08-30, Check-out: 2025-09-01 (overlaps Sept)
Linda Clark:         Check-in: 2025-08-31, Check-out: 2025-09-02 (overlaps Sept)
Robert Taylor:       Check-in: 2025-08-31, Check-out: 2025-09-03 (overlaps Sept)
Robert Taylor:       Check-in: 2025-08-31, Check-out: 2025-09-03 (overlaps Sept)
Maria Garcia:        Check-in: 2025-08-31, Check-out: 2025-09-03 (overlaps Sept)
```

### Why the Analytics CSV Was Correct:
The analytics aggregation likely uses proper date range overlap logic:
```sql
WHERE start_date <= '2025-11-30' AND end_date >= '2025-09-01'
```

## Solution Implemented

### Fix #1: Updated Filter Logic
Changed the filtering condition to include **all reservations that overlap the period**:

```python
# NEW CODE (CORRECT):
# Overlap condition: check_in <= end_date AND check_out >= start_date
filtered = [r for r in rs if r.check_in_date <= end_date and r.check_out_date >= start_date]
```

### Fix #2: Added SQLite Support
The function was only designed for CSV backend, but the system uses SQLite. Added SQLite query support:

```python
if reservations_path.suffix == '.db':
    # Use SQL query with proper date range overlap
    cursor.execute("""
        SELECT ...
        FROM reservations
        WHERE start_date <= ? AND end_date >= ?
        ORDER BY start_date
    """, (end_date, start_date))
```

### Fix #3: Updated UI Call
Modified `app/ui/main.py` to pass the correct path (database path for SQLite):

```python
# Pass db_path when using SQLite backend
if self.db_path:
    reservations = guest_reservation_detail_report(self.db_path, start, end)
else:
    reservations = guest_reservation_detail_report(self.paths.reservations, start, end)
```

## Verification Results

### Before Fix:
```
Reservations shown in UI: 252 (missing 7)
Reservations in CSV:      259 (correct)
Discrepancy:              7 reservations
```

### After Fix:
```
✅ Reservations shown in UI: 259 (all included)
✅ Reservations in CSV:      259 (correct)
✅ Discrepancy:              0 reservations

Breakdown:
  - 252 reservations with check-in dates in Sept-Nov
  - 7 reservations that checked in before Sept 1 but overlapped the period
  - Total: 259 reservations

Status Distribution:
  - Cancelled:   28
  - Checked-In:  4
  - Checked-Out: 191
  - Confirmed:   36

Total Revenue (Checked-Out + Checked-In): MYR 81,433.44
```

## Files Modified

1. **`app/reporting.py`**
   - Line 89-102: Updated `guest_reservation_detail_report()` function
   - Added SQLite backend support
   - Changed filter logic to include overlapping reservations

2. **`app/ui/main.py`**
   - Line ~1850: Updated `refresh_guest_detail_report()` to use db_path

## Impact

### Minimal Code Changes:
- ✅ Only 2 files modified
- ✅ ~30 lines of code changed
- ✅ Backward compatible with CSV backend
- ✅ No changes to database schema
- ✅ No changes to UI layout

### Business Impact:
- ✅ Reports now show complete data
- ✅ Consistent with analytics exports
- ✅ Accurate revenue calculations
- ✅ No missing guest information

## Testing

### Test Cases Verified:
1. ✅ Reservations with check-in dates in Sept-Nov: Included
2. ✅ Reservations that checked in before Sept 1 but checked out during period: **Now included**
3. ✅ Reservations completely outside the period: Correctly excluded
4. ✅ Edge cases (check-in on Aug 31, check-out on Sept 1): **Now included**
5. ✅ SQLite backend: Working correctly
6. ✅ CSV backend (if used): Still compatible

## Root Cause Category

**Type**: Logic Error - Incorrect date range filtering

**Severity**: Medium
- Not a data corruption issue
- Not a security issue
- Caused incomplete reporting (7 out of 259 records missing = 2.7% error rate)

**Complexity**: Low
- Simple logic fix
- Well-defined problem
- Minimal code changes required

## Lessons Learned

1. **Date Range Filtering**: When filtering by date ranges, always consider:
   - Reservations that **start** within the range
   - Reservations that **end** within the range
   - Reservations that **span** the range (start before, end after)
   - Use overlap condition: `start <= range_end AND end >= range_start`

2. **Consistency**: Ensure all reporting functions use the same date filtering logic

3. **Backend Abstraction**: When supporting multiple backends (CSV + SQLite), ensure all functions work with both

## Recommendation

Consider adding a unit test to prevent regression:

```python
def test_overlapping_reservations():
    """Test that reservations overlapping the period are included."""
    # Create test data with reservation checking in before range
    # but checking out during range
    # Assert it's included in the report
```

---

**Fix Applied**: November 14, 2025  
**Status**: ✅ Complete and Verified  
**Files Changed**: 2 (reporting.py, main.py)  
**Lines Changed**: ~30 lines  
**Test Result**: PASS (259 reservations found, matching analytics CSV)
