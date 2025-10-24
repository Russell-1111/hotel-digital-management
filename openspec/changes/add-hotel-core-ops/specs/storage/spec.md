## ADDED Requirements

### Requirement: CSV Data Storage
The system SHALL persist data to CSV files with the following specifications:
- rooms.csv columns: room_id,room_type,base_price
- reservations.csv columns: reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at
- Date format: ISO (YYYY-MM-DD); Currency: MYR

#### Scenario: Initialize storage directory
- **WHEN** the application starts
- **THEN** it ensures the data directory and required CSV files exist (creating headers if missing)

### Requirement: Atomic Writes and Locking
The system SHALL prevent data corruption and double-booking via file locking and atomic write operations.

#### Scenario: Serialized reservation writes
- **WHEN** creating or modifying a reservation
- **THEN** the system acquires a file lock, re-validates availability, writes the change to a temp file, and atomically replaces the original

### Requirement: Automatic Backups
The system SHALL perform automatic daily backups.

#### Scenario: Nightly backup at 02:30 local time
- **WHEN** the local time reaches 02:30
- **THEN** the system copies CSV files to `backups/` with a timestamped filename
- **AND** retains only the last 7 days of backups
