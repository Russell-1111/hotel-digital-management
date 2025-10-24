## Why
Digitize core front-desk operations for a single ~20-room boutique hotel to replace manual processes. Goals: prevent double-booking with real-time status, compute totals correctly (10% service charge + 6% tax, MYR), and provide daily/monthly reports. Operate offline on Windows with CSV storage and a Tkinter UI.

## What Changes
- Add capabilities and initial implementation plan for:
  - Reservations: create/modify/cancel; same-day bookings; status transitions
  - Rooms: static inventory; derived status (Available, Reserved, Occupied)
  - Billing: calculate totals with 10% service charge then 6% tax; MYR currency
  - Reporting: daily check-in/out lists; monthly revenue summaries (on-screen)
  - Storage: CSV persistence, file locking, automatic backups at 02:30 (retain 7 days)
  - UI: Tkinter desktop screens for front desk operators
- Defaults and conventions:
  - Date format: ISO (YYYY-MM-DD); local hotel time for 14:00 check-in, 11:00 check-out
  - Files: rooms.csv and reservations.csv under a configurable data directory
  - No external integrations in MVP

## Impact
- Affected specs: reservations, rooms, billing, reporting, storage
- Affected systems/modules: ui (Tkinter), storage (CSV + backups), core services
- No breaking changes (greenfield)
