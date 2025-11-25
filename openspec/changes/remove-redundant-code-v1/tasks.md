## 1. Phase 1: Remove Unused Imports
- [ ] 1.1 Remove unused `List` import from `app/analytics.py` (line 10)
- [ ] 1.2 Remove unused `re`, `Optional`, `time`, `timedelta` imports from `app/reservations.py` (lines 1-6)
- [ ] 1.3 Remove unused `dataclass`, `datetime`, `Dict` imports from `app/reporting.py` (lines 1-4)
- [ ] 1.4 Remove unused `mdates` import from `app/visualization.py` (line 14)
- [ ] 1.5 Remove unused `sys`, `datetime`, `timedelta`, `timezone` imports from `app/ui/main.py` (lines 2-7)
- [ ] 1.6 Run full test suite: `pytest tests/ -v`
- [ ] 1.7 Verify no import errors in logs

## 2. Phase 2: Remove Dead Functions
- [ ] 2.1 Remove `auto_status_transitions` function from `app/reservations.py` (lines 395-407)
- [ ] 2.2 Remove `auto_status_transitions` import from `app/ui/main.py` (line 28)
- [ ] 2.3 Remove `auto_status_transitions` call from `app/ui/main.py` (line 1256-1259)
- [ ] 2.4 Run full test suite: `pytest tests/ -v`
- [ ] 2.5 Perform manual smoke test of reservation workflow (create, modify, cancel)

## 3. Phase 3: Verification and Documentation
- [ ] 3.1 Manual review: Check all Tkinter `command=` bindings in `app/ui/main.py` for removed symbols
- [ ] 3.2 Manual review: Check all `.bind()` calls in `app/ui/main.py` for removed symbols
- [ ] 3.3 Run test suite with coverage: `pytest tests/ --cov=app --cov-report=html`
- [ ] 3.4 Verify coverage report shows no missing lines due to removed code
- [ ] 3.5 Check application logs for any runtime import errors
- [ ] 3.6 Update CHANGELOG (if exists) with cleanup summary

## 4. Phase 4: Handle Diagnostic Script (Optional)
- [ ] 4.1 Review `tests/inspect_tkcalendar.py` purpose with team
- [ ] 4.2 Either: Move to `scripts/inspect_tkcalendar.py` OR add module-level docstring explaining diagnostic purpose
- [ ] 4.3 If moved to scripts/, verify pytest no longer attempts to run it

## 5. Post-Implementation
- [ ] 5.1 Commit changes with message: `chore: remove redundant imports and dead code`
- [ ] 5.2 Create PR with link to this proposal
- [ ] 5.3 Request code review with focus on safety verification
- [ ] 5.4 Merge after approval and CI passes
- [ ] 5.5 Monitor production logs for 24 hours post-deployment
