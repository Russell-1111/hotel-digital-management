# Proposal: Remove Redundant Code (v1)

## Why

Over time, the codebase has accumulated redundant code artifacts that impact maintainability and code clarity:
- **Unused imports** increase cognitive load and may confuse developers about actual dependencies
- **Dead functions** (e.g., `auto_status_transitions` in `reservations.py` with empty implementation) clutter the codebase
- **Unreferenced variables and imports** (e.g., `re` module imported but never used in `reservations.py`) waste namespace and may suggest incorrect dependencies

Removing these artifacts will improve code efficiency, reduce potential confusion, and make the codebase more maintainable.

## What Changes

This proposal targets safe removal of:

1. **Unused imports** across all modules:
   - `analytics.py`: Remove unused `List` import
   - `reservations.py`: Remove unused `re`, `Optional`, `time`, `timedelta`, `timezone` imports
   - `reporting.py`: Remove unused `dataclass`, `datetime`, `Dict` imports
   - `visualization.py`: Remove unused `mdates` import
   - `ui/main.py`: Remove unused `sys`, `datetime`, `timedelta`, `timezone`, `auto_status_transitions` import

2. **Dead code** removal:
   - `reservations.py`: Remove `auto_status_transitions()` function (empty implementation, functionality moved to application layer)
   - `tests/inspect_tkcalendar.py`: This is a diagnostic script, not a test—consider moving to `scripts/` or documenting its purpose

3. **Verification safeguards**:
   - Ensure no dynamic invocations (e.g., via `getattr`, `eval`, Tkinter command bindings)
   - Run full test suite to confirm no regressions
   - Preserve all SQLite schema definitions and database operations

## Impact

### Affected Specs
- **code-quality** (NEW): Introduces requirements for maintaining clean, redundancy-free code

### Affected Code
- **app/analytics.py**: Remove unused import
- **app/reservations.py**: Remove 4 unused imports + 1 dead function
- **app/reporting.py**: Remove 3 unused imports
- **app/visualization.py**: Remove 1 unused import
- **app/ui/main.py**: Remove 4 unused imports + 1 unused function import
- **tests/inspect_tkcalendar.py**: Relocate or document (not a regression risk)

### Risks
- **Low risk**: Changes are mechanical removals verified by Pylance static analysis
- **Mitigation**: Full test suite execution before merging; manual review of Tkinter event bindings

### Dependencies
None. This is a standalone cleanup change.
