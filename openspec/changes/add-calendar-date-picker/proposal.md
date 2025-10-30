# Add Calendar Date Picker to All Date Input Fields

## Why
Currently, all date input fields in the application are plain text entries requiring manual typing in YYYY-MM-DD format. This is error-prone and requires users to remember the exact format. Adding calendar picker widgets alongside manual entry will reduce input errors, improve user experience, and speed up data entry for front desk staff.

## What Changes
- Add calendar picker widgets to all date input fields throughout the UI
- Maintain existing manual text input capability for power users
- Use minimal code with lightweight, native-looking calendar widget (tkcalendar.DateEntry)
- Apply consistent styling across all date inputs
- Affected date fields:
  - Daily Operations tab: Date selection for check-in/check-out lists
  - Reservations tab: Check-in and check-out date fields
  - Reservations tab (Modify dialog): Check-in and check-out date fields
  - Availability tab: Start and end date fields
  - Reports tab: Month input for revenue (YYYY-MM format)
  - Reports tab: Start and end date fields for guest reservation details

## Impact
- Affected specs: `ui`
- Affected code: `app/ui/main.py` (all date entry widgets)
- Dependencies: Add `tkcalendar` package to `requirements.txt`
- User experience: Improved date selection with visual calendar + preserved keyboard input
- No breaking changes: existing manual date entry still works
