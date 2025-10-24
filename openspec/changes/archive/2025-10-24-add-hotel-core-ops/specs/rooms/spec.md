## ADDED Requirements

### Requirement: Room Inventory
The system SHALL maintain a static inventory of rooms with the following fields:
- room_id, room_type, base_price
- Data source: rooms.csv

#### Scenario: Load inventory from CSV
- **WHEN** the application starts or the Rooms module is initialized
- **THEN** it loads `rooms.csv` from the configured data directory
- **AND** validates required columns exist (room_id, room_type, base_price)

### Requirement: Room Status Derivation
The system SHALL derive a room's status (Available, Reserved, Occupied) from reservations and the current local time.

#### Scenario: Status is Reserved when a confirmed future reservation exists
- **WHEN** a reservation with status "Confirmed" overlaps the queried date range for a room
- **THEN** the room status SHALL be reported as "Reserved" for that period

#### Scenario: Status is Occupied during active stay
- **WHEN** the current time is between the reservation's check-in (≥ 14:00 local) and before check-out time (11:00 local)
- **THEN** the room status SHALL be reported as "Occupied"

#### Scenario: Status is Available otherwise
- **WHEN** no overlapping active reservations exist for the given date
- **THEN** the room status SHALL be reported as "Available"
