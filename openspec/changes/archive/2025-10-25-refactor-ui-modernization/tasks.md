## 1. UI Modernization Implementation
- [x] 1.1 Establish ttk theme and base styles (fonts, paddings)
- [x] 1.2 Convert container layouts to grid with consistent spacing (8px)
- [x] 1.3 Ensure resizable window with reasonable min size; expand key widgets
- [x] 1.4 Add inline validation cues for date inputs and guest count
- [x] 1.5 Add status message/progress indicator for refresh/long tasks
- [x] 1.6 Show error dialogs with a hint to check the log file path
- [x] 1.7 Wire basic logging in `run.py` (TimedRotatingFileHandler, 7-day retention)
- [x] 1.8 Add a simple UI smoke test to ensure the app starts and tabs construct
- [x] 1.9 Update README (Logging section and brief UI notes)

## 2. Validation
- [x] 2.1 Visual check: consistent padding/spacing and fonts
- [x] 2.2 Validation feedback shows on invalid dates
- [x] 2.3 Window resize retains usable layout
- [x] 2.4 Logs written to `logs/app.log` and rotated daily

## 3. Delivery
- [x] 3.1 Ensure all tasks are completed and documented
- [x] 3.2 Mark tasks as done and request review/approval
- [x] 3.3 Archive change upon deployment and update stable specs if standards become permanent
