# ui Specification Delta

## ADDED Requirements

### Requirement: Reservation List Display Format
The system SHALL display reservation lists without showing internal reservation IDs to users.

- Reservation lists on the Reservations tab SHALL display: Room number, guest name, check-in/out dates, status, and total cost
- Format SHALL be: `"Room {room_id} | {guest_name} | {check_in_date}->{check_out_date} | {status} | MYR {total_cost}"`
- Reservation ID SHALL NOT be visible in the list display (remains internal for backend operations)
- List items SHALL use pipe (|) separators for visual clarity between fields
- Each field SHALL be separated by ` | ` (space-pipe-space) for consistent spacing

#### Scenario: Display reservation in list without ID
- **WHEN** the Reservations tab loads and populates the existing reservations list
- **THEN** each list item displays: `"Room {room_id} | {guest_name} | {check_in}->{check_out} | {status} | MYR {cost}"`
- **AND** the reservation ID is not visible to the user
- **AND** pipe separators clearly delimit each field

#### Scenario: Select and modify reservation without visible ID
- **WHEN** a user selects a reservation from the list and clicks "Modify Selected"
- **THEN** the system correctly identifies the reservation using internal ID mapping
- **AND** opens the modification dialog with pre-filled reservation details
- **AND** the user never sees or needs to know the reservation ID

#### Scenario: Select and cancel reservation without visible ID
- **WHEN** a user selects a reservation from the list and clicks "Cancel Selected"
- **THEN** the system correctly identifies the reservation using internal ID mapping
- **AND** cancels the correct reservation
- **AND** the user never sees or needs to know the reservation ID

### Requirement: Daily Operations List Display Format
The system SHALL display daily check-in and check-out lists without showing internal reservation IDs.

- Daily check-ins list SHALL display: Room number and guest name
- Daily check-outs list SHALL display: Room number and guest name
- Format SHALL be: `"Room {room_id} | {guest_name}"`
- Reservation ID SHALL NOT be visible in daily operations lists
- Simplified format appropriate for quick reference during daily operations

#### Scenario: Display check-ins without ID
- **WHEN** the Daily Ops tab loads and populates today's check-ins
- **THEN** each list item displays: `"Room {room_id} | {guest_name}"`
- **AND** the reservation ID is not visible
- **AND** the list is clean and easy to scan

#### Scenario: Display check-outs without ID
- **WHEN** the Daily Ops tab loads and populates today's check-outs
- **THEN** each list item displays: `"Room {room_id} | {guest_name}"`
- **AND** the reservation ID is not visible
- **AND** the list is clean and easy to scan
