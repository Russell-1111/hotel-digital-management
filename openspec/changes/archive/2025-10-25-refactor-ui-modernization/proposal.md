## Why
Front desk staff need a clearer, more consistent, and more accessible UI to reduce input errors and speed up daily operations. The current Tkinter screens use mixed layouts and minimal feedback. A focused modernization will improve usability without changing any business logic.

## What Changes
- Adopt ttk theming and consistent widget styles (accessible defaults; optional light/dark themes).
- Standardize layout using grid + consistent spacing/padding; enforce minimum window sizes and resizable behavior.
- Add user feedback mechanisms: status messages for long actions and error dialogs with a link/path to the log file.
- Improve input validation feedback (invalid dates/values show inline visual cues).
- Keep scope to UI layer only; no API or data model changes.
- Limit changes to <200 LOC total for a fast, low-risk improvement.

Non-breaking: No changes to CSV format, modules, or public function signatures.

## Impact
- Affected specs: ui
- Affected code: `app/ui/main.py` (layout/styles/feedback), `run.py` (logging hookup), optional small helpers.
- Tests: add/adjust minimal smoke tests for UI wiring.
