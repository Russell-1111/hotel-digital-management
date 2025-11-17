# Project Context

## Purpose
Hotel Digital Management System for a single boutique hotel (~20 rooms). The system digitizes reservation, check-in, and check-out workflows for front desk staff, prevents double-booking through real-time status tracking, automates stay cost calculations (with tax), and generates daily and monthly operational reports. Primary outcomes: fewer errors, faster desk operations, and reliable records.

## Tech Stack
- Language: Python 3.x
- UI: Tkinter desktop application (Windows)
- Storage: SQLite database (primary); legacy CSV support maintained
- Visualization: matplotlib (charts), pandas (data analysis)
- Packaging/Distribution: Local Windows installation
- Logging: Python `logging` with structured logs
- Config: INI file (`config.ini`) for settings

## Project Conventions

### Code Style
- Naming: `snake_case` for functions/variables, `PascalCase` for classes
- File naming: `snake_case.py` per module; group by feature (analytics, auth, reservations, rooms, reporting, storage, visualization, ui)
- Formatting: Black (line length ~100); optional Ruff or Flake8 linting
- Imports: absolute within package; standard library first, then third-party, then local
- Functions: target ≤ 50 lines; prefer pure functions for calculations
- Docstrings: Google-style or reST for public functions; type hints required

### Architecture Patterns
- Application architecture: Simple modular structure (modules: auth, analytics, reservations, rooms, reporting, storage, visualization, ui)
- Boundaries:
	- `auth`: authentication, password hashing, role-based access control
	- `analytics`: SQL-based revenue aggregation by room type with time bucketing
	- `reservations`: create/modify/cancel, availability checks, business rules, cost calculation (room rate + 10% service charge + 6% tax on subtotal)
	- `rooms`: static inventory, derived status (Available/Reserved/Occupied)
	- `reporting`: daily check-in/out lists; monthly revenue summaries
	- `storage`: CSV read/write with file locking (legacy); backup/restore routines
	- `storage_sqlite`: SQLite database operations with WAL mode and atomic transactions
	- `visualization`: matplotlib chart generation (trend, bar, combined) with PNG/CSV export
	- `ui`: Tkinter screens; calls into services via thin controllers
- Communication: in-process function calls (no network API)
- Error handling: central error types; top-level UI error dialog + safe fallbacks
- Logging: structured logs with timestamps via Python `logging`
- Configuration: `config.ini` for paths, backup time, check-in/out times, timezone, auth settings

### Data Model and Storage
- Primary Storage: SQLite database (`reservations.db`)
	- Tables: `rooms`, `reservations`, `users`
	- Atomic transactions with WAL mode
	- Timezone-aware timestamps (stored in UTC, displayed in hotel timezone)
- Legacy Storage: CSV files (deprecated but supported)
	- `rooms.csv`: Columns: `room_id,room_type,base_price,image_path`
	- `reservations.csv`: Columns: `reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at`
- Status derivation rules:
	- Available → Reserved on booking creation
	- Reserved → Occupied automatically at check-in date (14:00 by default)
	- Occupied → Available at check-out date/time (11:00 by default)
- Overbooking prevention: availability check reads current data + applies status derivation before confirming bookings; writes use database transactions to avoid race conditions.
- Backups: automatic daily backup of SQLite database to `backups/` with timestamped filenames; run at 02:30 local time; retain last 7 days.
- Date/Time format: ISO (YYYY-MM-DD) for dates; timezone-aware datetimes stored in UTC; use local hotel time for transitions (14:00 check-in, 11:00 check-out)
- Currency: MYR (display in UI and reports)

### Testing Strategy
- Framework: Pytest
- Unit tests: pricing/tax calculations (in reservations); date/status transitions; database operations; analytics aggregation
- Integration tests: reservation flow with SQLite; backup/restore; CSV migration
- UI tests: minimal smoke via small presenters/controllers (logic separated from Tkinter views)
- Coverage target: 70%+ overall; must include auth, reservations, and analytics modules
- Conventions: AAA pattern (Arrange-Act-Assert); factory helpers for test data

### Git Workflow
- Strategy: Trunk-based development
- Branch naming: `feat/…`, `fix/…`, `chore/…`, `docs/…`, `refactor/…`
- Commits: Conventional Commits (e.g., `feat(reservations): allow same-day bookings`)
- PRs: Small, focused; at least one reviewer; CI must pass tests/linters
- Releases: lightweight tags; changelog generated from commits

## Domain Context

### Hotel Operations Terminology
- Room Types: e.g., Standard, Deluxe (configurable per hotel)
- Room Status: Available, Reserved, Occupied (derived from reservations + time)
- Booking Status: Confirmed, Cancelled, Checked-In, Checked-Out
- Guest Type: Walk-in (same-day) or Reserved

### Business Rules
- Standard check-in: 14:00; standard check-out: 11:00
- Same-day bookings allowed if room is Available for current date; walk-ins treated as immediate assignments
- Cancellations: set reservation status to "Cancelled" and free room immediately
- Modifications: either direct change if dates/room remain valid; otherwise treat as cancellation + new booking
- Overbooking prevention: enforce atomic availability check + write; deny double-booking

### Key Workflows
1. Reservation: Search availability → Select room → Create reservation → Confirm (compute total with 10% service charge, then 6% tax; currency MYR)
2. Check-in: Auto-transition to Occupied at check-in date/time (or manual override)
3. Check-out: Auto-transition to Available at check-out time; finalize stay record
4. Reporting: Daily check-in/out lists; monthly revenue summary

## Important Constraints

### Business Constraints
- Single property; internal use by front desk staff
- No external system integrations
- On-device operation (no internet required)

### Technical Constraints
- SQLite database storage (single-file, serverless)
- Windows desktop environment
- Database transactions for data consistency
- Automatic daily backups (retain 7 days)

### Performance Requirements
- Optimized for a single operator at a time
- Inventory size: ~20 rooms
- Typical daily operations: dozens of reservations/check-ins/check-outs

## External Dependencies

### Required Integrations
None at this time.

### Third-Party Services
Not applicable.
