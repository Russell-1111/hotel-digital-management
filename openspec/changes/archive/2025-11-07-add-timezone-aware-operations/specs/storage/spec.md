## ADDED Requirements

### Requirement: Timezone Configuration
The system SHALL support configurable hotel timezone via `config.ini` to enable portable scheduling and timezone-aware operations.

#### Scenario: Load valid IANA timezone from config
- **WHEN** `config.ini` contains `[ops]` section with `timezone = Asia/Kuala_Lumpur`
- **THEN** the system loads the timezone using Python's `zoneinfo` module
- **AND** all time-based operations use this timezone for hotel local time interpretations

#### Scenario: Reject invalid timezone gracefully
- **WHEN** `config.ini` contains an invalid timezone name (e.g., `timezone = Invalid/Timezone`)
- **THEN** the system fails to start with a clear error message
- **AND** the error message includes the invalid value and a reference to valid IANA timezone names (e.g., link to Wikipedia tz database list)

#### Scenario: Timezone independence from server OS
- **WHEN** the server's operating system timezone is set to UTC
- **AND** the hotel's configured timezone is `Asia/Kuala_Lumpur`
- **THEN** scheduled operations (backups, status transitions) trigger at times corresponding to hotel's local timezone, not server's OS timezone

### Requirement: Timezone-Aware Timestamp Storage
The system SHALL store all timestamp fields in UTC with explicit timezone markers, following ISO 8601 format.

#### Scenario: Generate UTC timestamps for new records
- **WHEN** creating or updating a reservation
- **THEN** the system sets `created_at` and `updated_at` fields to current UTC time
- **AND** formats timestamps as ISO 8601 with `Z` suffix (e.g., `2025-11-07T10:30:00Z`)

#### Scenario: Parse and validate timezone-aware timestamps
- **WHEN** reading timestamps from the database or CSV files
- **THEN** the system parses them as UTC timestamps
- **AND** validates that timestamps include timezone information
- **AND** converts to hotel timezone for display purposes when needed

## MODIFIED Requirements

### Requirement: Automatic Backups
The system SHALL perform automatic daily backups of the database at the configured time in the hotel's timezone.

#### Scenario: Nightly database backup at 02:30 hotel local time
- **WHEN** the current time in the hotel's configured timezone reaches 02:30
- **THEN** the system copies the database file to `backups/` with a timestamped filename (e.g., `20251107-023000-reservations.db`)
- **AND** uses atomic file operations (temp file + rename) to prevent corruption
- **AND** retains only the last 7 days of backups
- **AND** the backup triggers at 02:30 hotel local time regardless of server timezone or DST transitions

#### Scenario: Backup timestamp uses UTC
- **WHEN** performing a backup
- **THEN** the backup filename timestamp reflects the backup time in the server's local timezone (for filesystem compatibility)
- **AND** backup metadata stored in logs uses UTC timestamps with timezone markers

#### Scenario: Backup includes WAL and SHM files if present
- **WHEN** performing a backup and WAL mode is enabled
- **THEN** the system also copies `.db-wal` and `.db-shm` files if they exist
- **OR** performs a checkpoint before backup to consolidate WAL into main DB file

### Requirement: Naive Timestamp Migration
The system SHALL automatically migrate existing naive timestamps to UTC format on first startup with timezone-aware version.

#### Scenario: Detect and migrate naive timestamps
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

#### Scenario: Migration assumes configured timezone
- **WHEN** migrating naive timestamps
- **THEN** the system assumes all naive timestamps were created in the hotel's currently configured timezone
- **AND** logs a warning if any timestamp is more than 1 year in the past or future (likely anomaly)
- **AND** allows optional override via `migration_source_timezone` config parameter for edge cases

### Requirement: Timezone Utility Functions
The system SHALL provide reusable utility functions for timezone conversions and timestamp generation.

#### Scenario: Get current UTC time
- **WHEN** the application needs the current time for timestamping operations
- **THEN** a utility function `now_utc()` returns timezone-aware datetime in UTC

#### Scenario: Get current hotel local time
- **WHEN** the application needs to display or check the current time in hotel's timezone
- **THEN** a utility function `now_hotel(tz)` returns timezone-aware datetime in the hotel's configured timezone

#### Scenario: Convert between UTC and hotel timezone
- **WHEN** converting timestamps between UTC storage format and hotel local time for display or scheduling
- **THEN** utility functions `to_utc(dt, tz)` and `to_hotel_tz(dt_utc, tz)` perform conversions
- **AND** preserve the instant in time (only timezone changes, not the absolute moment)
