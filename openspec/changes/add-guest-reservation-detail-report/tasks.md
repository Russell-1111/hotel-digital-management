# Implementation Tasks

## 1. Backend Implementation
- [x] 1.1 Add `guest_reservation_detail_report()` function in `app/reporting.py` to filter reservations by date range
- [x] 1.2 Ensure function returns list of reservations with all required fields (guest_name, room_id, check_in_date, check_out_date, total_cost, num_guests)
- [x] 1.3 Add helper to compute derived fields: number of nights, room rate per night (if needed for display)

## 2. UI Implementation
- [x] 2.1 Extend Reports tab in `app/ui/main.py` with new section for "Guest Reservation Details"
- [x] 2.2 Add date range inputs (start date, end date) with default to current month
- [x] 2.3 Add "Generate Report" button to trigger report generation
- [x] 2.4 Display results in a Treeview/table with columns: Guest Name, Room ID, Check-In, Check-Out, Room Rate, Nights, Total Cost
- [x] 2.5 Add summary row displaying grand total of all listed reservations
- [x] 2.6 Ensure layout does not interfere with existing monthly revenue summary

## 3. Testing
- [x] 3.1 Write unit test for `guest_reservation_detail_report()` with sample reservations
- [x] 3.2 Test edge cases: empty date range, no reservations, multiple reservations spanning different rooms
- [x] 3.3 Manual UI testing: verify table displays correctly, filters work, totals are accurate

## 4. Documentation
- [x] 4.1 Update README.md or user documentation if needed to describe new report feature
