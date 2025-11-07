## ADDED Requirements

### Requirement: Users Table Schema
The system SHALL extend the database schema to include a `users` table for storing authentication credentials and role information.

#### Scenario: Initialize users table
- **WHEN** `init_schema()` is called
- **THEN** the system creates a `users` table if it does not exist
- **AND** the table has columns: `username TEXT PRIMARY KEY`, `password_hash TEXT NOT NULL`, `role TEXT NOT NULL`, `created_at TEXT NOT NULL`, `updated_at TEXT NOT NULL`
- **AND** a CHECK constraint enforces `role IN ('admin', 'staff')`

#### Scenario: Users table schema validation
- **WHEN** the database schema is initialized
- **THEN** the `users` table primary key is `username` (unique, not null)
- **AND** the `password_hash` column stores password hashes in format `"salt_hex:hash_hex"`
- **AND** the `role` column only accepts values 'admin' or 'staff'
- **AND** `created_at` and `updated_at` store ISO8601 UTC timestamps with 'Z' suffix

#### Scenario: Existing installations add users table
- **WHEN** an existing installation upgrades to a version with authentication
- **THEN** `init_schema()` executes `CREATE TABLE IF NOT EXISTS users (...)`
- **AND** the users table is added without affecting existing `rooms` or `reservations` tables
- **AND** no data migration is required (fresh table starts empty)

### Requirement: Check User Existence
The system SHALL provide a way to check if any users exist in the database for initial setup flow.

#### Scenario: Check if users table is empty
- **WHEN** the application needs to determine if initial setup is required
- **THEN** a query `SELECT COUNT(*) FROM users` is executed
- **AND** if the count is 0, the application knows no users exist
- **AND** if the count is > 0, at least one user exists

#### Scenario: No users exist on first run
- **WHEN** the application starts for the first time after installation
- **THEN** the users table exists but has 0 rows
- **AND** the application triggers the initial setup flow to create the first admin account
