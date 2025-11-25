## ADDED Requirements

### Requirement: Code Cleanliness
The codebase SHALL maintain clean code by prohibiting unused imports, dead functions, and unreferenced variables.

#### Scenario: Unused Import Detection
- **WHEN** a developer introduces an import that is not referenced in the module
- **THEN** static analysis tools (Pylance, linters) MUST flag the unused import
- **AND** the import MUST be removed before merging

#### Scenario: Dead Function Identification
- **WHEN** a function has no implementation (only `pass` statement) and is not part of a public API or abstract interface
- **THEN** the function MUST be removed along with all call sites
- **AND** a comment explaining the removal reason MUST be added if the function was previously documented

#### Scenario: Import Verification
- **WHEN** code review is performed
- **THEN** reviewers MUST verify that all imports are actively used in the module
- **AND** no imports exist solely for side effects (unless explicitly documented)

### Requirement: Static Analysis Integration
The development workflow SHALL use static analysis to detect code cleanliness violations.

#### Scenario: Pylance Unused Import Check
- **WHEN** a Python module is edited
- **THEN** Pylance's `source.unusedImports` refactoring MUST be available to developers
- **AND** unused imports MUST be identified and removed before commit

#### Scenario: Pre-Commit Validation
- **WHEN** code is committed (future enhancement)
- **THEN** a pre-commit hook MAY run static analysis checks
- **AND** reject commits with unused imports or obvious dead code

### Requirement: Safe Refactoring Process
Code cleanup operations SHALL follow a phased approach with verification at each stage.

#### Scenario: Phased Cleanup with Test Gates
- **WHEN** unused code is identified for removal
- **THEN** changes MUST be grouped into logical phases (e.g., Phase 1: Imports, Phase 2: Functions)
- **AND** the full test suite MUST pass after each phase before proceeding
- **AND** manual verification MUST be performed for dynamic invocations (e.g., Tkinter callbacks)

#### Scenario: Dynamic Code Safety Check
- **WHEN** removing a function or import
- **THEN** the developer MUST verify the symbol is not referenced dynamically via:
  - Tkinter command bindings (e.g., `Button(command=callback)`)
  - `getattr()`, `eval()`, or similar dynamic lookups
  - String-based dispatching or plugin systems
- **AND** if dynamic references exist, the removal MUST be deferred or refactored

#### Scenario: Rollback on Test Failure
- **WHEN** tests fail after a cleanup phase
- **THEN** changes from that phase MUST be rolled back immediately
- **AND** the cause of failure MUST be investigated before retrying

### Requirement: Documentation of Diagnostic Code
Diagnostic and debugging scripts SHALL be clearly distinguished from automated tests.

#### Scenario: Diagnostic Script Identification
- **WHEN** a script in `tests/` directory is not a pytest-compatible test
- **THEN** the script MUST either:
  - Be moved to `scripts/` directory with a descriptive name, OR
  - Include a module-level docstring explaining its diagnostic purpose
- **AND** the script MUST NOT be executed as part of the automated test suite

#### Scenario: Test vs. Diagnostic Distinction
- **WHEN** reviewing test files
- **THEN** files named `test_*.py` MUST contain pytest-compatible test functions
- **AND** diagnostic/inspection tools MUST be named without the `test_` prefix or reside in `scripts/`
