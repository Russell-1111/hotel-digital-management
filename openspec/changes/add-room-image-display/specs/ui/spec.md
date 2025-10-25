# ui Specification Deltas

## ADDED Requirements

### Requirement: Room Image Display in Dropdown
The system SHALL display thumbnail images of rooms in the room selection dropdown on the Reservations tab.

#### Scenario: Display room thumbnails in dropdown
- **WHEN** the room selection dropdown is populated with available rooms
- **THEN** each dropdown item SHALL include a thumbnail image (80x60 pixels) of the room
- **AND** the thumbnail SHALL appear alongside the room text (number, type, price)
- **AND** rooms without images SHALL display a placeholder thumbnail

#### Scenario: Update thumbnails when availability changes
- **WHEN** the user clicks "Check Availability" to refresh the room list
- **THEN** the dropdown SHALL reload and display updated room thumbnails
- **AND** image loading SHALL not block the UI thread
- **AND** previously loaded images SHALL be reused if available in cache

### Requirement: Room Image Display in Availability List
The system SHALL display larger preview images of rooms in the Availability tab listing.

#### Scenario: Display room preview images in availability list
- **WHEN** the Availability tab shows the list of rooms and their status
- **THEN** each room entry SHALL include a preview image (320x240 pixels)
- **AND** the preview image SHALL appear aligned with the room status text
- **AND** rooms without images SHALL display a larger placeholder image

#### Scenario: Handle image loading errors gracefully
- **WHEN** a room image fails to load due to file system errors
- **THEN** the UI SHALL display the placeholder image instead
- **AND** the room selection/display SHALL remain functional
- **AND** a warning SHALL be logged but no error dialog shown to the user

### Requirement: Image Memory Management
The system SHALL manage loaded room images efficiently to prevent memory leaks.

#### Scenario: Cache room images to prevent garbage collection
- **WHEN** room images are loaded for display in Tkinter widgets
- **THEN** PhotoImage objects SHALL be stored in a persistent cache
- **AND** the cache SHALL prevent images from being garbage collected while in use
- **AND** the cache SHALL be cleared and refreshed when room data is reloaded

#### Scenario: Reuse cached images on refresh
- **WHEN** the user triggers a refresh of room lists or availability
- **THEN** already-loaded room images SHALL be reused from cache
- **AND** only new or changed images SHALL be loaded from disk
- **AND** unnecessary image reloading SHALL be avoided to improve performance
