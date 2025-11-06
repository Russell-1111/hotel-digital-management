# Storage Delta Specification

## MODIFIED Requirements

### Requirement: Data Persistence
The system SHALL persist data to an SQLite database with the following specifications:
- Database file: `data/reservations.db`
- Rooms table schema:
  - `room_id TEXT PRIMARY KEY`
  - `room_type TEXT NOT NULL`
  - `base_price REAL NOT NULL`
  - `image_path TEXT DEFAULT ''`
- Reservations table schema:
  - `id TEXT PRIMARY KEY`
  - `room_id TEXT NOT NULL` (foreign key to rooms)
  - `guest_name TEXT NOT NULL`
  - `guest_phone TEXT NOT NULL`
  - `guest_email TEXT NOT NULL`
  - `start_date TEXT NOT NULL` (ISO8601: YYYY-MM-DD)
  - `end_date TEXT NOT NULL` (ISO8601: YYYY-MM-DD)
  - `num_guests INTEGER NOT NULL`
  - `status TEXT NOT NULL` (Confirmed|Cancelled|Checked-In|Checked-Out)
  - `total_cost REAL NOT NULL`
  - `created_at TEXT NOT NULL` (ISO8601 timestamp)
  - `updated_at TEXT NOT NULL` (ISO8601 timestamp)
- Schema metadata table:
  - `schema_info(version INTEGER, migrated_at TEXT)`
- Index for availability queries: `idx_reservations_availability(room_id, start_date, end_date)`
- SQLite pragmas: `journal_mode=WAL`, `foreign_keys=ON`

#### Scenario: Initialize database schema
- **WHEN** the application starts and `data/reservations.db` does not exist
- **THEN** the system creates the database file with all required tables, indexes, and schema_info
- **AND** sets schema version to 1

#### Scenario: Automatic CSV migration on first run
- **WHEN** `data/reservations.db` does not exist but `data/rooms.csv` and `data/reservations.csv` exist
- **THEN** the system creates the SQLite database, migrates all CSV data to respective tables
- **AND** logs migration summary to console (e.g., "Migrated 15 rooms, 42 reservations")
- **AND** preserves original CSV files in `data/` directory
- **AND** records migration timestamp in schema_info table

### Requirement: Transaction-Based Writes
The system SHALL use SQLite transactions to ensure atomic, consistent writes and prevent data corruption.

#### Scenario: Create reservation with transaction
- **WHEN** creating a new reservation
- **THEN** the system begins a transaction, validates room availability via indexed query, inserts the reservation record, and commits
- **AND** if any step fails, the transaction is rolled back and no changes persist

#### Scenario: Modify reservation with transaction
- **WHEN** modifying an existing reservation (dates, room, or guest info)
- **THEN** the system begins a transaction, validates new availability if needed, updates the record, and commits
- **AND** uses parameterized SQL to prevent injection

#### Scenario: Cancel reservation with transaction
- **WHEN** cancelling a reservation
- **THEN** the system begins a transaction, updates status to "Cancelled", sets updated_at timestamp, and commits

### Requirement: Indexed Availability Queries
The system SHALL use database indexes to efficiently check room availability.

#### Scenario: Fast availability check for date range
- **WHEN** checking if a room is available for a given date range
- **THEN** the query uses the `idx_reservations_availability` index to find overlapping reservations
- **AND** returns results in O(log n) time complexity for n reservations

### Requirement: Automatic Backups
The system SHALL perform automatic daily backups of the SQLite database.

#### Scenario: Nightly database backup at 02:30 local time
- **WHEN** the local time reaches 02:30
- **THEN** the system copies `data/reservations.db` to `backups/` with a timestamped filename (e.g., `20251106-023000-reservations.db`)
- **AND** uses atomic file operations (temp file + rename) to prevent corruption
- **AND** retains only the last 7 days of backups

#### Scenario: Backup includes WAL and SHM files if present
- **WHEN** performing a backup and WAL mode is enabled
- **THEN** the system also copies `.db-wal` and `.db-shm` files if they exist
- **OR** performs a checkpoint before backup to consolidate WAL into main DB file

## ADDED Requirements

### Requirement: CSV Export Capability
The system SHALL provide a function to export current database state to CSV files for legacy compatibility and reporting.

#### Scenario: Export database to CSV
- **WHEN** the `export_csv()` function is called with target directory path
- **THEN** the system writes `rooms.csv` and `reservations.csv` with current database contents
- **AND** CSV files match the original format (headers and column order preserved)
- **AND** uses atomic writes to prevent partial/corrupted exports

### Requirement: Storage Backend Configuration
The system SHALL support configurable storage backend selection via `config.ini`.

#### Scenario: SQLite backend selected by default
- **WHEN** the application starts and `config.ini` has `[storage]` section with `use_sqlite = true`
- **THEN** the system loads `app/storage_sqlite.py` backend
- **AND** all storage operations use SQLite transactions

#### Scenario: CSV backend fallback for compatibility
- **WHEN** the application starts and `config.ini` has `[storage]` section with `use_sqlite = false`
- **THEN** the system loads the original CSV-based backend
- **AND** all storage operations use file-locking and atomic CSV writes

### Requirement: Migration Validation and Logging
The system SHALL validate data integrity during CSV→SQLite migration and log detailed results.

#### Scenario: Validate migrated data matches source
- **WHEN** CSV migration completes
- **THEN** the system counts total rows migrated per table
- **AND** logs summary to console: "Migration complete: 15 rooms, 42 reservations"
- **AND** logs detailed migration info to `logs/app.log` with timestamp

#### Scenario: Handle migration errors gracefully
- **WHEN** CSV migration encounters invalid data (e.g., malformed date, missing required field)
- **THEN** the system logs the specific error with row details
- **AND** continues migration for remaining valid rows
- **OR** aborts migration and deletes incomplete `.db` file if critical errors occur (e.g., schema creation failure)

### Requirement: Standalone Migration Script
The system SHALL provide a standalone CLI script for manual CSV→SQLite migration.

#### Scenario: Run migration script manually
- **WHEN** running `python scripts/migrate_csv_to_sqlite.py --data-dir data --output data/reservations.db`
- **THEN** the script reads CSV files from specified directory, creates SQLite database at output path
- **AND** validates all data and prints summary report
- **AND** exits with code 0 on success, non-zero on failure

#### Scenario: Migration script with dry-run mode
- **WHEN** running `python scripts/migrate_csv_to_sqlite.py --dry-run`
- **THEN** the script validates CSV data and reports what would be migrated
- **AND** does not create or modify any database files
- **AND** prints validation errors and warnings
