# reservations Specification

## Purpose
TBD - created by archiving change add-hotel-core-ops. Update Purpose after archive.
## Requirements
### Requirement: Reservation Management
The system SHALL allow front desk staff to create, retrieve, modify, and cancel reservations with the following fields:
- reservation_id, room_id, guest_name, phone, email, check_in_date, check_out_date, num_guests, status, total_cost, created_at, updated_at.

#### Scenario: Create reservation when room is available
- **WHEN** a reservation is requested for a room and date range with no conflicting active reservations
- **THEN** the system creates the reservation with status "Confirmed" and persists it to the database
- **AND** the room status is considered "Reserved" for the booked date range
- **AND** `created_at` and `updated_at` are set to current UTC time with timezone marker

#### Scenario: Prevent double-booking
- **WHEN** a reservation is requested that overlaps an existing active reservation for the same room
- **THEN** the system SHALL reject the request with an availability error

### Requirement: Same-Day Bookings
The system SHALL support same-day bookings with immediate assignment if the room is available.

#### Scenario: Same-day booking success
- **WHEN** the booking is for the current date and the desired room has no conflicting active reservation
- **THEN** create the reservation immediately and mark the room as "Reserved" until check-in time

#### Scenario: Same-day booking unavailable
- **WHEN** the booking is for the current date but the room is already Reserved or Occupied for any overlapping time
- **THEN** the system SHALL reject the request with an availability error

### Requirement: Reservation Status Transitions
The system SHALL update reservation and room statuses based on configured times interpreted in the hotel's timezone.

#### Scenario: Auto transition to Occupied at check-in time
- **WHEN** the current time in the hotel's configured timezone reaches 14:00 on the reservation's check_in_date
- **THEN** the reservation status transitions to "Checked-In"
- **AND** the room status becomes "Occupied"
- **AND** `updated_at` is set to current UTC time with timezone marker

#### Scenario: Auto transition to Available at check-out time
- **WHEN** the current time in the hotel's configured timezone reaches 11:00 on the reservation's check_out_date
- **THEN** the reservation status transitions to "Checked-Out"
- **AND** the room status becomes "Available"
- **AND** `updated_at` is set to current UTC time with timezone marker

#### Scenario: Cancel reservation frees room
- **WHEN** a reservation is cancelled
- **THEN** the reservation status is set to "Cancelled"
- **AND** the room is immediately available for new bookings over those dates
- **AND** `updated_at` is set to current UTC time with timezone marker

### Requirement: Timezone-Aware Operations
The system SHALL use the configured hotel timezone to determine when to transition reservation statuses, storing all timestamps in UTC while interpreting check-in and check-out times in the hotel's local timezone.

#### Scenario: Status transitions independent of server timezone
- **WHEN** the server is located in a different timezone than the hotel (e.g., server in UTC, hotel in Asia/Kuala_Lumpur)
- **AND** the current UTC time corresponds to 14:00 in the hotel's configured timezone on the reservation's check_in_date
- **THEN** the system transitions the reservation status to "Checked-In"
- **AND** updates the `updated_at` timestamp in UTC format with timezone marker (e.g., `2025-11-07T06:00:00Z`)

#### Scenario: DST transition handling
- **WHEN** the hotel's timezone observes daylight saving time transitions
- **AND** a status transition is scheduled during the DST transition period
- **THEN** the system correctly handles the time shift and triggers transitions at the intended local time

#### Scenario: Naive timestamp migration
- **WHEN** the application starts for the first time after upgrade with existing reservations containing naive timestamps
- **AND** the naive timestamps lack timezone information (e.g., `2025-11-01T10:30:00`)
- **THEN** the system interprets naive timestamps as being in the hotel's configured timezone
- **AND** converts them to UTC with explicit timezone marker (e.g., `2025-11-01T02:30:00Z` for Asia/Kuala_Lumpur)
- **AND** stores migration completion flag to prevent re-running migration
- **AND** logs migration summary: "Migrated N naive timestamps from [timezone] to UTC"

