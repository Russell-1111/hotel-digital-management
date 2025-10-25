# Add Room Image Display

## Why
The front desk staff need visual references of each room to better assist guests during the booking process. Currently, room selection displays only text information (room number, type, price), which makes it difficult for staff to describe rooms to guests or help them choose appropriate accommodations. Adding room images will improve the booking experience and reduce booking errors.

## What Changes
- Add image file path field to room data model and CSV storage
- Store room images in a dedicated `images/rooms/` directory
- Display thumbnail images (80x60px) in the room selection dropdown (Reservations tab)
- Display larger preview images (320x240px) in the Availability tab listing
- Implement graceful fallback to placeholder image when room image is missing or fails to load
- Support common image formats (JPG, PNG)
- Pre-populate with images for rooms 101, 102, 103, 104

## Impact
- **Affected specs**: `rooms`, `ui`
- **Affected code**: 
  - `app/rooms.py` - Add image_path field to Room dataclass; update load_rooms()
  - `data/rooms.csv` - Add image_path column
  - `app/ui/main.py` - Update room dropdown and availability list to display images
  - New directory: `images/rooms/` for storing room photos
- **Data migration**: Existing rooms.csv will need an image_path column added; backward-compatible (empty paths handled gracefully)
- **User impact**: Improved visual room selection; no breaking changes to existing workflows
