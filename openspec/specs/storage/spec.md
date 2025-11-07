# storage Specification

## Purpose
TBD - created by archiving change add-hotel-core-ops. Update Purpose after archive.
## Requirements
### Requirement: CSV Data Storage
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

### Requirement: Atomic Writes and Locking
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

### Requirement: Automatic Backups
The system SHALL perform automatic daily backups of the SQLite database at the configured time in the hotel's timezone.

#### Scenario: Nightly database backup at 02:30 hotel local time
- **WHEN** the current time in the hotel's configured timezone reaches 02:30
- **THEN** the system copies `data/reservations.db` to `backups/` with a timestamped filename (e.g., `20251106-023000-reservations.db`)
- **AND** uses atomic file operations (temp file + rename) to prevent corruption
- **AND** retains only the last 7 days of backups
- **AND** the backup triggers at 02:30 hotel local time regardless of server timezone or DST transitions

#### Scenario: Backup filename uses local timestamp
- **WHEN** performing a backup
- **THEN** the backup filename timestamp reflects the backup time in the hotel's timezone (for filesystem compatibility)
- **AND** backup metadata stored in logs uses UTC timestamps with timezone markers

#### Scenario: Backup includes WAL and SHM files if present
- **WHEN** performing a backup and WAL mode is enabled
- **THEN** the system also copies `.db-wal` and `.db-shm` files if they exist
- **OR** performs a checkpoint before backup to consolidate WAL into main DB file

### Requirement: Indexed Availability Queries
The system SHALL use database indexes to efficiently check room availability.

#### Scenario: Fast availability check for date range
- **WHEN** checking if a room is available for a given date range
- **THEN** the query uses the `idx_reservations_availability` index to find overlapping reservations
- **AND** returns results in O(log n) time complexity for n reservations

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

### Requirement: Timezone Configuration
The system SHALL support configurable hotel timezone via `config.ini` to enable portable scheduling and timezone-aware operations.

#### Scenario: Load timezone from configuration
- **WHEN** `config.ini` contains `[ops]` section with `timezone = Asia/Kuala_Lumpur`
- **THEN** the system loads the timezone using Python's `zoneinfo` module
- **AND** all time-based operations use this timezone for hotel local time interpretations

#### Scenario: Invalid timezone validation
- **WHEN** `config.ini` contains an invalid timezone name (e.g., `timezone = Invalid/Timezone`)
- **THEN** the system fails to start with a clear error message
- **AND** the error message includes the invalid value and a reference to valid IANA timezone names (e.g., link to Wikipedia tz database list)

#### Scenario: Server timezone independence
- **WHEN** the server's operating system timezone is set to UTC
- **AND** the hotel's configured timezone is `Asia/Kuala_Lumpur`
- **THEN** scheduled operations (backups, status transitions) trigger at times corresponding to hotel's local timezone, not server's OS timezone

### Requirement: UTC Timestamp Storage
The system SHALL store all timestamp fields in UTC with explicit timezone markers, following ISO 8601 format.

#### Scenario: Create timestamps in UTC
- **WHEN** creating or updating a reservation
- **THEN** the system sets `created_at` and `updated_at` fields to current UTC time
- **AND** formats timestamps as ISO 8601 with `Z` suffix (e.g., `2025-11-07T10:30:00Z`)

#### Scenario: Parse and validate timestamps
- **WHEN** reading timestamps from the database or CSV files
- **THEN** the system parses them as UTC timestamps
- **AND** validates that timestamps include timezone information
- **AND** converts to hotel timezone for display purposes when needed

### Requirement: Naive Timestamp Migration
The system SHALL automatically migrate existing naive timestamps to UTC format on first startup with timezone-aware version.

#### Scenario: Automatic migration on first startup
- **WHEN** the application starts and the migration completion flag is not set
- **AND** existing records contain timestamps without timezone information (e.g., `2025-11-01T10:30:00`)
- **THEN** the system parses each naive timestamp and interprets it as being in the hotel's configured timezone
- **AND** converts each timestamp to UTC and adds timezone marker (e.g., `2025-11-01T02:30:00Z` for Asia/Kuala_Lumpur UTC+8)
- **AND** updates all affected records in the database
- **AND** stores migration completion flag in schema metadata table
- **AND** logs migration summary: "Migrated N reservations from naive to UTC timestamps"

#### Scenario: Skip migration if already completed
- **WHEN** the application starts and the migration completion flag is set
- **THEN** the system skips naive timestamp migration
- **AND** proceeds with normal startup

#### Scenario: Migration with validation warnings
- **WHEN** migrating naive timestamps
- **THEN** the system assumes all naive timestamps were created in the hotel's currently configured timezone
- **AND** logs a warning if any timestamp is more than 1 year in the past or future (likely anomaly)
- **AND** allows optional override via `migration_source_timezone` config parameter for edge cases

### Requirement: Timezone Utility Functions
The system SHALL provide reusable utility functions for timezone conversions and timestamp generation.

#### Scenario: Get current UTC time
- **WHEN** the application needs the current time for timestamping operations
- **THEN** a utility function `now_utc()` returns timezone-aware datetime in UTC

#### Scenario: Get current hotel time
- **WHEN** the application needs to display or check the current time in hotel's timezone
- **THEN** a utility function `now_hotel(tz)` returns timezone-aware datetime in the hotel's configured timezone

#### Scenario: Convert between timezones
- **WHEN** converting timestamps between UTC storage format and hotel local time for display or scheduling
- **THEN** utility functions `to_utc(dt, tz)` and `to_hotel_tz(dt_utc, tz)` perform conversions
- **AND** preserve the instant in time (only timezone changes, not the absolute moment)

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

