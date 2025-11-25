# Design: Remove Redundant Code (v1)

## Context

The Hotel Digital Management System has evolved through multiple feature additions (authentication, analytics, SQLite migration). During this evolution, some imports and functions became obsolete but were not removed:

- **Pylance static analysis** identified unused imports across 5 modules
- **Code inspection** revealed `auto_status_transitions()` function with empty implementation (note in code states: "Status transitions are handled by the application layer")
- **Test structure** includes a diagnostic script (`inspect_tkcalendar.py`) that's not a proper test

This cleanup is straightforward and low-risk because:
1. Static analysis tools (Pylance) definitively identify unused imports
2. The dead function has zero implementation and is only called once (can be safely removed)
3. All changes are mechanical deletions without behavioral modifications

## Goals / Non-Goals

### Goals
- Remove all unused imports identified by Pylance static analysis
- Remove dead code (`auto_status_transitions` function)
- Maintain 100% test pass rate
- Document safety verification approach for future cleanup efforts

### Non-Goals
- Refactoring module structure or architecture
- Adding new linting rules to CI/CD (future consideration)
- Optimizing performance (this is purely code hygiene)
- Removing commented code (none found in current audit)

## Decisions

### Decision 1: Use Pylance as Source of Truth
**Rationale**: Pylance's `source.unusedImports` refactoring is production-grade and accounts for:
- Dynamic imports via `__all__`
- Type hints and forward references
- Tkinter command bindings (callback strings)

**Alternatives Considered**:
- Manual inspection: Error-prone, time-consuming
- Other linters (flake8, ruff): Less integrated with Python language server

**Choice**: Trust Pylance analysis, but verify with test execution

### Decision 2: Remove `auto_status_transitions` Function
**Rationale**: 
- Function body is `pass` (no-op)
- Comment in code confirms: "This function currently does not persist changes. Status transitions are handled by the application layer."
- Only one call site in `ui/main.py` (line 1256) that can be removed

**Alternatives Considered**:
- Keep function as placeholder: Adds no value, misleads readers
- Deprecate with warning: Overkill for internal function

**Choice**: Remove entirely (function and call site)

### Decision 3: Phased Implementation with Test Checkpoints
**Rationale**: Minimize risk by allowing rollback at each phase

**Phases**:
1. **Phase 1 (Imports)**: Remove unused imports, run tests
2. **Phase 2 (Dead Functions)**: Remove `auto_status_transitions`, run tests
3. **Phase 3 (Verification)**: Manual review of Tkinter bindings, final test run

### Decision 4: Handle `tests/inspect_tkcalendar.py` Separately
**Rationale**: This is a diagnostic/debugging script, not a unit test. It should either:
- Move to `scripts/` directory, OR
- Add docstring explaining its purpose as a debugging tool

**Choice**: Document in tasks but leave relocation as optional (not blocking)

## Safety Analysis

### Static Safety
All identified removals are validated by:
- **Pylance** `source.unusedImports` refactoring (no false positives in our analysis)
- **grep searches** for symbol usage across codebase
- **Code usage analysis** via `list_code_usages` tool

### Dynamic Safety
Potential risks from dynamic invocations:
- **Tkinter command bindings**: `Button(command="function_name")` or `bind("<event>", callback)`
- **`getattr()` / `eval()` usage**: None found in codebase
- **Pickle/serialization**: Not used in this project

**Verification**: Manual review of all Tkinter `command=` and `bind()` calls in `ui/main.py` to confirm removed imports are not referenced.

### Test Coverage Safety
Current test coverage for affected modules:
- `app/analytics.py`: Covered by `test_analytics.py`
- `app/reservations.py`: Covered by `test_storage_sqlite.py` (integration tests)
- `app/reporting.py`: Covered by `test_reporting.py`
- `app/visualization.py`: Covered by `test_visualization.py`
- `app/ui/main.py`: Minimal coverage (`test_ui.py` only tests import)

**Mitigation**: Run full test suite after each phase. If UI test coverage is insufficient, consider manual smoke test of reservation flow.

## Migration Plan

### Pre-Implementation
1. ✅ Run Pylance analysis on all modules
2. ✅ Document all unused imports and dead code
3. ✅ Verify test coverage for affected modules

### Implementation (Phased)
**Phase 1: Remove Unused Imports**
- Modules: `analytics.py`, `reservations.py`, `reporting.py`, `visualization.py`, `ui/main.py`
- Verification: Run `pytest` after changes
- Rollback: `git checkout <file>` if tests fail

**Phase 2: Remove Dead Function**
- Remove `auto_status_transitions` function from `reservations.py`
- Remove import and call site from `ui/main.py`
- Verification: Run `pytest` + manual check of reservation workflow
- Rollback: `git checkout` both files if issues arise

**Phase 3: Final Verification**
- Review all Tkinter event bindings for removed symbols
- Run full test suite with coverage report
- Check logs for any runtime import errors

### Post-Implementation
- Update documentation (if `auto_status_transitions` was documented anywhere)
- Consider adding pre-commit hook for unused imports (future work)

## Risks / Trade-offs

### Risk 1: Pylance False Negatives
**Likelihood**: Very Low  
**Impact**: Low (test suite would catch actual usage)  
**Mitigation**: Full test suite execution + manual review

### Risk 2: Tkinter Dynamic Callback References
**Likelihood**: Very Low (Tkinter uses object references, not string names in this codebase)  
**Impact**: Medium (UI would break)  
**Mitigation**: Manual review of `ui/main.py` command bindings

### Risk 3: Hidden Dependencies in Tests
**Likelihood**: Very Low (Pylance scans test files too)  
**Impact**: Medium (tests would fail)  
**Mitigation**: Run tests after each phase

## Open Questions

None. Analysis is complete and approach is straightforward.
