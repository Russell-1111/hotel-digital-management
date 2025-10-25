# Implementation Tasks

## 1. Data Model and Storage
- [x] 1.1 Add `image_path` field to Room dataclass in `app/rooms.py`
- [x] 1.2 Update `load_rooms()` to read image_path from CSV (default to empty string if missing)
- [x] 1.3 Add `image_path` column to `data/rooms.csv` with paths for rooms 101-104
- [x] 1.4 Create `images/rooms/` directory structure
- [x] 1.5 Add placeholder image `images/rooms/placeholder.png` (simple gray box with "No Image" text)

## 2. Image Management Utilities
- [x] 2.1 Create helper function `load_room_image(image_path, size)` in `app/rooms.py` to load and resize images
- [x] 2.2 Implement fallback to placeholder for missing/invalid image paths
- [x] 2.3 Cache loaded PhotoImage objects to prevent garbage collection issues

## 3. UI Integration - Reservations Tab
- [x] 3.1 Modify room dropdown to display thumbnail images (80x60px) alongside room text
- [x] 3.2 Update `refresh_available_rooms()` to load and cache room images
- [x] 3.3 Test dropdown display with mixed image availability (some rooms with images, some without)

## 4. UI Integration - Availability Tab
- [x] 4.1 Update availability list to show larger preview images (320x240px) for each room
- [x] 4.2 Modify `refresh_availability()` to include room images in display
- [x] 4.3 Ensure images align properly with room status text

## 5. Testing and Validation
- [x] 5.1 Add unit tests for `load_room_image()` function (valid path, invalid path, missing file)
- [x] 5.2 Test UI rendering with all rooms having images
- [x] 5.3 Test UI rendering with some rooms missing images (placeholder fallback)
- [x] 5.4 Verify image memory management (no leaks during repeated refreshes)
- [x] 5.5 Test with actual room photos for rooms 101, 102, 103, 104

## 6. Documentation
- [x] 6.1 Update `data/rooms.csv` header documentation (if exists)
- [x] 6.2 Add comment in code explaining image path conventions
- [x] 6.3 Validate spec compliance with `openspec validate add-room-image-display --strict`
