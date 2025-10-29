# Remove Reservation ID Display

## Why
Reservation IDs are internal system identifiers that clutter the UI and provide no value to front desk staff. Removing them from the visible reservation lists improves readability and reduces visual noise, allowing staff to focus on relevant information (guest name, room, dates, status, cost).

## What Changes
- Remove reservation ID from the "Existing Reservations" list display on the Reservations tab
- Remove reservation ID from the Daily Check-Ins and Check-Outs lists on the Daily Ops tab
- Maintain internal ID parsing logic for modify/cancel operations (IDs still needed for backend operations but hidden from user)
- Update list item format to start with room number instead of reservation ID

## Impact
- **Affected specs**: `ui`
- **Affected code**: `app/ui/main.py` (reservation list formatting and parsing logic)
- **User-visible change**: Reservation lists will be cleaner and easier to read
- **Backend impact**: None - IDs still used internally for operations
