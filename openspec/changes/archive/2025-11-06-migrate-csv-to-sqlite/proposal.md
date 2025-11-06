# Proposal: Migrate CSV to SQLite Storage

## Why
The current CSV-based storage relies on file locking and atomic writes to prevent race conditions and data corruption. While functional for single-user scenarios, CSV lacks transactional guarantees, indexing for efficient queries, and schema enforcement. Migrating to SQLite provides ACID transactions, better concurrency control, indexed queries for availability checks, and preserves the single-file simplicity without external database dependencies.

## What Changes
- Create new `app/storage_sqlite.py` module implementing SQLite backend with same public API as current CSV storage
- Add automatic one-time CSV→SQLite migration on first run (if `.db` doesn't exist but `.csv` files do)
- Replace CSV file-locking with SQLite transactions for write operations
- Add indexed query support for room availability checks (indexed on `room_id`, `start_date`, `end_date`)
- Provide backward compatibility shim in `app/storage.py` with config flag `use_sqlite` (default: True)
- Preserve CSV export capability via new `export_csv()` helper for reporting/backups
- Update backup mechanism to copy `.db` file atomically instead of CSV files
- Update tests to use temporary SQLite databases with proper cleanup

## Impact
- **Affected specs**: `storage` (MODIFIED: data persistence, backup, locking mechanisms)
- **Affected code**:
  - `app/storage.py` - Modified to act as compatibility shim/wrapper
  - `app/storage_sqlite.py` - New module (primary implementation)
  - `scripts/migrate_csv_to_sqlite.py` - New standalone migration script
  - `config.ini` - Add `[storage]` section with `use_sqlite = true`
  - `tests/test_storage.py` - Update to test SQLite backend
  - `tests/test_reservations.py` - Update to use temp SQLite DB
  - Other test files using storage layer
- **Breaking changes**: None (backward compatible via shim; automatic migration)
- **Dependencies**: Python stdlib `sqlite3` only (no new external dependencies)
