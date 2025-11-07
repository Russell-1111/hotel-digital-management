## ADDED Requirements

### Requirement: Timezone-Aware Status Transitions
The system SHALL use the configured hotel timezone to determine when to transition reservation statuses, storing all timestamps in UTC while interpreting check-in and check-out times in the hotel's local timezone.

#### Scenario: Status transition at hotel local time regardless of server timezone
- **WHEN** the server is located in a different timezone than the hotel (e.g., server in UTC, hotel in Asia/Kuala_Lumpur)
- **AND** the current UTC time corresponds to 14:00 in the hotel's configured timezone on the reservation's check_in_date
- **THEN** the system transitions the reservation status to "Checked-In"
- **AND** updates the `updated_at` timestamp in UTC format with timezone marker (e.g., `2025-11-07T06:00:00Z`)

#### Scenario: DST-safe scheduling
- **WHEN** the hotel's timezone observes daylight saving time transitions
- **AND** a status transition is scheduled during the DST transition period
- **THEN** the system correctly handles the time shift and triggers transitions at the intended local time

#### Scenario: Timestamp migration on first startup
- **WHEN** the application starts for the first time after upgrade with existing reservations containing naive timestamps
- **AND** the naive timestamps lack timezone information (e.g., `2025-11-01T10:30:00`)
- **THEN** the system interprets naive timestamps as being in the hotel's configured timezone
- **AND** converts them to UTC with explicit timezone marker (e.g., `2025-11-01T02:30:00Z` for Asia/Kuala_Lumpur)
- **AND** stores migration completion flag to prevent re-running migration
- **AND** logs migration summary: "Migrated N naive timestamps from [timezone] to UTC"

## MODIFIED Requirements

### Requirement: Reservation Management
The system SHALL allow front desk staff to create, retrieve, modify, and cancel reservations with the following fields:
- reservation_id, room_id, guest_name, phone, email, check_in_date, check_out_date, num_guests, status, total_cost, created_at, updated_at.
- All timestamp fields (`created_at`, `updated_at`) SHALL be stored in UTC with ISO 8601 format including timezone marker (e.g., `2025-11-07T10:30:00Z`).
- Date fields (`check_in_date`, `check_out_date`) remain as date-only strings (`YYYY-MM-DD`) representing dates in the hotel's local calendar.

#### Scenario: Create reservation when room is available
- **WHEN** a reservation is requested for a room and date range with no conflicting active reservations
- **THEN** the system creates the reservation with status "Confirmed" and persists it to the database
- **AND** the room status is considered "Reserved" for the booked date range
- **AND** `created_at` and `updated_at` are set to current UTC time with timezone marker

#### Scenario: Prevent double-booking
- **WHEN** a reservation is requested that overlaps an existing active reservation for the same room
- **THEN** the system SHALL reject the request with an availability error

### Requirement: Reservation Status Transitions
The system SHALL update reservation and room statuses based on configured times interpreted in the hotel's timezone.

#### Scenario: Auto transition to Occupied at check-in time in hotel timezone
- **WHEN** the current time in the hotel's configured timezone reaches 14:00 on the reservation's check_in_date
- **THEN** the reservation status transitions to "Checked-In"
- **AND** the room status becomes "Occupied"
- **AND** `updated_at` is set to current UTC time with timezone marker

#### Scenario: Auto transition to Available at check-out time in hotel timezone
- **WHEN** the current time in the hotel's configured timezone reaches 11:00 on the reservation's check_out_date
- **THEN** the reservation status transitions to "Checked-Out"
- **AND** the room status becomes "Available"
- **AND** `updated_at` is set to current UTC time with timezone marker

#### Scenario: Cancel reservation frees room
- **WHEN** a reservation is cancelled
- **THEN** the reservation status is set to "Cancelled"
- **AND** the room is immediately available for new bookings over those dates
- **AND** `updated_at` is set to current UTC time with timezone marker
