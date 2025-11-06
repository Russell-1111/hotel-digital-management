# Implementation Tasks

## 1. Core SQLite Implementation
- [x] 1.1 Create `app/storage_sqlite.py` with schema initialization functions
- [x] 1.2 Implement `ensure_db()` to create database and tables with indexes
- [x] 1.3 Implement `read_rooms()` function returning list of Room objects
- [x] 1.4 Implement `read_reservations()` function returning list of Reservation objects
- [x] 1.5 Implement `write_reservation()` with transaction support and parameterized SQL
- [x] 1.6 Implement `update_reservation()` with transaction support
- [x] 1.7 Implement `delete_reservation()` with transaction support
- [x] 1.8 Implement `is_room_available()` using indexed query
- [x] 1.9 Enable SQLite pragmas (WAL mode, foreign keys)
- [x] 1.10 Implement `connection.row_factory = sqlite3.Row` for dict-like access

## 2. CSV Migration Logic
- [x] 2.1 Implement `migrate_from_csv()` function in `storage_sqlite.py`
- [x] 2.2 Add CSV file detection logic (check if .csv exists but .db doesn't)
- [x] 2.3 Parse and validate CSV data before insertion
- [x] 2.4 Implement batch insert with transaction for rooms table
- [x] 2.5 Implement batch insert with transaction for reservations table
- [x] 2.6 Add migration validation: count rows, verify FK constraints
- [x] 2.7 Record migration timestamp in schema_info table
- [x] 2.8 Add comprehensive logging for migration process (console + file)
- [x] 2.9 Preserve original CSV files after successful migration
- [x] 2.10 Handle migration errors gracefully with rollback

## 3. Configuration and Shim Layer
- [x] 3.1 Update `config.ini` to add `[storage]` section with `use_sqlite = true`
- [x] 3.2 Modify `app/rooms.py` AppConfig dataclass to include `use_sqlite: bool`
- [x] 3.3 Update `load_config()` to parse storage.use_sqlite from config
- [x] 3.4 Refactor `app/storage.py` to act as shim/wrapper
- [x] 3.5 Implement conditional import: load `storage_sqlite` if `use_sqlite=true`, else keep CSV logic
- [x] 3.6 Re-export all public functions from selected backend
- [x] 3.7 Add deprecation notice for CSV backend (comment/docstring)

## 4. Backup Mechanism Updates
- [x] 4.1 Modify `backup_now()` to detect backend type from config
- [x] 4.2 Implement SQLite backup: copy `.db` file atomically to backups/
- [x] 4.3 Handle WAL/SHM files: checkpoint before backup to consolidate
- [x] 4.4 Update backup retention logic to clean old `.db` files
- [x] 4.5 Preserve CSV backup code path for backward compatibility

## 5. CSV Export Capability
- [x] 5.1 Implement `export_csv(output_dir: Path)` in `storage_sqlite.py`
- [x] 5.2 Query all rooms and write to `rooms.csv` with correct headers
- [x] 5.3 Query all reservations and write to `reservations.csv` with correct headers/column order
- [x] 5.4 Use atomic writes (temp file + rename) for CSV export
- [x] 5.5 Add logging for export operations

## 6. Standalone Migration Script
- [x] 6.1 Create `scripts/migrate_csv_to_sqlite.py` with argparse CLI
- [x] 6.2 Add command-line arguments: `--data-dir`, `--output`, `--dry-run`, `--verbose`
- [x] 6.3 Implement dry-run mode: validate CSV without creating DB
- [x] 6.4 Implement actual migration: call `migrate_from_csv()` with validation
- [x] 6.5 Add detailed progress logging and error reporting
- [x] 6.6 Return appropriate exit codes (0=success, 1=error)
- [x] 6.7 Add usage documentation in script docstring

## 7. Integration with Existing Modules
- [x] 7.1 Update `app/reservations.py` imports if needed (should be transparent via shim)
- [x] 7.2 Update `app/rooms.py` to ensure Room objects work with both backends
- [x] 7.3 Update `app/reporting.py` to use shim layer (no direct backend calls)
- [x] 7.4 Verify `app/ui/main.py` works without changes (uses reservations/rooms modules)

## 8. Testing - Unit Tests
- [x] 8.1 Create `tests/test_storage_sqlite.py` with temp DB fixture
- [x] 8.2 Test schema creation and initialization
- [x] 8.3 Test read/write operations for rooms and reservations
- [x] 8.4 Test transaction rollback on error
- [x] 8.5 Test parameterized SQL (no injection)
- [x] 8.6 Test indexed availability query performance
- [x] 8.7 Test CSV migration with sample data
- [x] 8.8 Test CSV export round-trip (DB→CSV→DB)
- [x] 8.9 Test migration validation and error handling
- [x] 8.10 Test migration idempotency (don't re-migrate if DB exists)

## 9. Testing - Integration Tests
- [x] 9.1 Update `tests/test_reservations.py` to use temp SQLite DB via config override
- [x] 9.2 Update `tests/test_storage.py` to test both backends with feature flags
- [x] 9.3 Test reservation creation with SQLite backend
- [x] 9.4 Test double-booking prevention with SQLite transactions
- [x] 9.5 Test reservation modification with availability recheck
- [x] 9.6 Test cancellation and status transitions
- [x] 9.7 Test auto-status transitions with SQLite
- [x] 9.8 Test backup mechanism with SQLite files
- [x] 9.9 Test concurrent operations (if applicable)
- [x] 9.10 Add test cleanup: delete temp DB files after each test

## 10. Documentation and Comments
- [x] 10.1 Add comprehensive docstrings to all functions in `storage_sqlite.py`
- [x] 10.2 Document transaction handling patterns with inline comments
- [x] 10.3 Document migration steps with inline comments
- [x] 10.4 Add README section explaining SQLite migration
- [x] 10.5 Update USER_GUIDE.md with SQLite backend information
- [x] 10.6 Add migration troubleshooting guide
- [x] 10.7 Document rollback procedure in case of issues
- [x] 10.8 Add code comments explaining WAL mode and checkpoint operations

## 11. Validation and Quality Assurance
- [x] 11.1 Run full test suite with `use_sqlite=false` (baseline CSV)
- [x] 11.2 Run full test suite with `use_sqlite=true` (new SQLite)
- [x] 11.3 Compare test results to ensure behavior parity
- [ ] 11.4 Manual testing: create/modify/cancel reservations via UI
- [ ] 11.5 Manual testing: verify double-booking prevention
- [ ] 11.6 Manual testing: run migration script on production-like CSV data
- [ ] 11.7 Performance testing: availability queries with 100+ reservations
- [ ] 11.8 Performance testing: backup operations with large DB
- [x] 11.9 Verify logs contain migration details and no errors
- [x] 11.10 Code review: check for SQL injection vulnerabilities

## 12. Deployment Preparation
- [x] 12.1 Update default `config.ini` template with `[storage]` section
- [ ] 12.2 Add migration notice to app startup logs
- [ ] 12.3 Test first-run migration on clean environment
- [ ] 12.4 Verify CSV files preserved after migration
- [ ] 12.5 Test rollback: switch config to CSV backend and verify operation
- [ ] 12.6 Prepare deployment checklist/runbook
- [ ] 12.7 Create backup of current CSV data before deployment
