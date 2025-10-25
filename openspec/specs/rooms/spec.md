# rooms Specification

## Purpose
TBD - created by archiving change add-hotel-core-ops. Update Purpose after archive.
## Requirements
### Requirement: Room Inventory
The system SHALL maintain a static inventory of rooms with the following fields:
- room_id, room_type, base_price, image_path
- Data source: rooms.csv
- The image_path field SHALL contain a relative path to the room's image file (e.g., "images/rooms/101.jpg") or be empty if no image is available

#### Scenario: Load inventory from CSV
- **WHEN** the application starts or the Rooms module is initialized
- **THEN** it loads `rooms.csv` from the configured data directory
- **AND** validates required columns exist (room_id, room_type, base_price)
- **AND** reads the optional image_path column (defaulting to empty string if column is missing)

#### Scenario: Load inventory with image paths
- **WHEN** the rooms.csv contains an image_path column with valid paths
- **THEN** each Room object SHALL include the image_path value
- **AND** empty or missing image paths SHALL default to an empty string

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

### Requirement: Room Image Loading
The system SHALL provide a function to load and resize room images for display in the UI.

#### Scenario: Load valid room image
- **WHEN** a room has a valid image_path pointing to an existing JPG or PNG file
- **THEN** the image SHALL be loaded from the filesystem
- **AND** resized to the requested dimensions while maintaining aspect ratio
- **AND** returned as a Tkinter PhotoImage object

#### Scenario: Handle missing room image
- **WHEN** a room has an empty image_path or the file does not exist
- **THEN** a placeholder image SHALL be loaded instead
- **AND** the placeholder SHALL be resized to the requested dimensions
- **AND** no error SHALL be raised to the caller

#### Scenario: Handle invalid image format
- **WHEN** a room's image_path points to a file that cannot be loaded as an image
- **THEN** a placeholder image SHALL be used as fallback
- **AND** a warning SHALL be logged indicating the invalid image path

