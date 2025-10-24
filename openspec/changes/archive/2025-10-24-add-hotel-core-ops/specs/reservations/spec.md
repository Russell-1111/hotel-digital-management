## ADDED Requirements

### Requirement: Reservation Management
The system SHALL allow front desk staff to create, retrieve, modify, and cancel reservations with the following fields:
- reservation_id, room_id, guest_name, phone, email, check_in_date, check_out_date, num_guests, status, total_cost, created_at, updated_at.

#### Scenario: Create reservation when room is available
- **WHEN** a reservation is requested for a room and date range with no conflicting active reservations
- **THEN** the system creates the reservation with status "Confirmed" and persists it to reservations.csv
- **AND** the room status is considered "Reserved" for the booked date range

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
The system SHALL update reservation and room statuses based on configured times.

#### Scenario: Auto transition to Occupied at check-in time
- **WHEN** the current local time reaches 14:00 on the reservation's check_in_date
- **THEN** the reservation status transitions to "Checked-In"
- **AND** the room status becomes "Occupied"

#### Scenario: Auto transition to Available at check-out time
- **WHEN** the current local time reaches 11:00 on the reservation's check_out_date
- **THEN** the reservation status transitions to "Checked-Out"
- **AND** the room status becomes "Available"

#### Scenario: Cancel reservation frees room
- **WHEN** a reservation is cancelled
- **THEN** the reservation status is set to "Cancelled"
- **AND** the room is immediately available for new bookings over those dates
