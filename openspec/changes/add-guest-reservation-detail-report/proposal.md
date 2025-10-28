# Change Proposal: Guest Reservation Detail Report

## Why
The current Reports tab only displays monthly revenue totals without detailed breakdown. Front desk staff need visibility into individual guest reservations, including check-in/check-out dates, room assignments, and per-reservation costs to verify billing, answer guest inquiries, and audit revenue calculations.

## What Changes
- Add a new "Guest Reservation Details" report to the Reports tab
- Display tabular list of reservations with columns: Guest Name, Room ID, Check-In Date, Check-Out Date, Room Rate, Number of Nights, Total Cost
- Support filtering by date range (start date to end date)
- Show per-reservation totals and a grand total at the bottom
- Preserve existing monthly revenue summary functionality

## Impact
- Affected specs: `reporting`, `ui`
- Affected code: `app/reporting.py` (new function), `app/ui/main.py` (Reports tab UI)
- Benefits: Better transparency for billing verification and guest service
- No breaking changes
