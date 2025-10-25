# Room Images Directory

This directory contains images for each hotel room.

## Naming Convention
- Images should be named using the room ID: `{room_id}.jpg` or `{room_id}.png`
- Example: `101.jpg`, `102.jpg`, `103.jpg`, `104.jpg`

## Image Specifications
- **Supported formats**: JPG, PNG
- **Recommended size**: 1280x960 pixels (4:3 aspect ratio) or similar
- **Thumbnail display**: 80x60 pixels (in room dropdown)
- **Preview display**: 320x240 pixels (in availability list)

## Current Room Assignments
- **101.jpg** - Room 101 (Standard)
- **102.jpg** - Room 102 (Deluxe)
- **103.jpg** - Room 103 (Standard)
- **104.jpg** - Room 104 (Suite)

## Adding New Room Images
1. Save the room photo in this directory
2. Name it using the room ID (e.g., `105.jpg`)
3. Update `data/rooms.csv` to include the image path: `images/rooms/105.jpg`
4. Restart the application to load the new image

## Placeholder Image
If a room does not have an image, the system will display a placeholder image automatically.
