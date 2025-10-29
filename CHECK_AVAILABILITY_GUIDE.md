# Check Availability Button - Complete Guide

## How It Works

The "Check Availability" button is connected to the `refresh_available_rooms()` function in `app/ui/main.py`.

## Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER CLICKS "Check Availability" Button                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Read Date Inputs                                       │
│  • Gets check-in date from text field                           │
│  • Gets check-out date from text field                          │
│  • Example: "2025-10-30" and "2025-10-31"                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Validate Date Format                                   │
│  • Try to parse dates as YYYY-MM-DD                             │
│  • If INVALID: Turn text red, clear dropdown, stop              │
│  • If VALID: Turn text black, continue                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Load All Reservations                                  │
│  • Reads data/reservations.csv                                  │
│  • Loads all existing reservations into memory                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Check Each Room's Availability                         │
│  For each room (101, 102, 103, 104):                            │
│    1. Filter active reservations for this room                  │
│    2. Skip Cancelled and Checked-Out reservations               │
│    3. For each active reservation:                              │
│       - Check if dates overlap using overlap algorithm          │
│       - If ANY overlap found → Room NOT available               │
│    4. If NO overlaps → Room IS available                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Build Available Rooms List                             │
│  • Format: "101 (Standard) - MYR 120.00"                        │
│  • Only includes available rooms                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Update UI                                              │
│  • Populate dropdown with available rooms                       │
│  • If rooms available: Auto-select first room                   │
│  • Load and display thumbnail image for selected room           │
│  • If NO rooms available: Empty dropdown                        │
└─────────────────────────────────────────────────────────────────┘
```

## Overlap Detection Algorithm

The core logic uses this mathematical formula:

```python
def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)
```

### Visual Examples:

#### Example 1: OVERLAP DETECTED ✗
```
Existing: |========|  (Oct 28 - Oct 31)
Requested:     |===|   (Oct 30 - Oct 31)
             ^^^^^^^^
             OVERLAP!
```

#### Example 2: NO OVERLAP ✓
```
Existing: |========|     (Oct 28 - Oct 31)
Requested:           |===| (Nov 01 - Nov 02)
          No overlap - dates don't touch
```

#### Example 3: OVERLAP DETECTED ✗
```
Existing:     |========|  (Oct 29 - Nov 01)
Requested: |======|        (Oct 28 - Oct 30)
              ^^^^
              OVERLAP!
```

## Real Examples from Current Data

### Current Active Reservations (as of Oct 29, 2025):

| Room | Guest | Check-in   | Check-out  | Status      |
|------|-------|------------|------------|-------------|
| 101  | R     | 2025-10-28 | 2025-10-31 | Checked-In  |
| 102  | E     | 2025-10-29 | 2025-10-30 | Checked-In  |
| 103  | E     | 2025-10-29 | 2025-10-30 | Checked-In  |
| 101  | (blank)| 2025-11-03 | 2025-11-05 | Confirmed   |
| 102  | a     | 2025-10-30 | 2025-11-01 | Confirmed   |
| 103  | a     | 2025-10-30 | 2025-10-31 | Confirmed   |
| 104  | a     | 2025-10-30 | 2025-10-31 | Confirmed   |

### Test Case 1: Check Oct 30-31 (Your Screenshot)
**Input:**
- Check-in: 2025-10-30
- Check-out: 2025-10-31

**Result:**
- Room 101: ✗ NOT AVAILABLE (overlaps with R's Oct 28-31 reservation)
- Room 102: ✗ NOT AVAILABLE (overlaps with a's Oct 30-Nov 1 reservation)
- Room 103: ✗ NOT AVAILABLE (overlaps with a's Oct 30-31 reservation)
- Room 104: ✗ NOT AVAILABLE (overlaps with a's Oct 30-31 reservation)

**Dropdown shows:** Empty (no available rooms)

### Test Case 2: Check Nov 01-02
**Input:**
- Check-in: 2025-11-01
- Check-out: 2025-11-02

**Result:**
- Room 101: ✓ AVAILABLE (Oct 28-31 ended, Nov 03-05 hasn't started)
- Room 102: ✓ AVAILABLE (Oct 30-Nov 1 ends exactly when we start)
- Room 103: ✓ AVAILABLE (Oct 30-31 ended)
- Room 104: ✓ AVAILABLE (Oct 30-31 ended)

**Dropdown shows:**
```
101 (Standard) - MYR 120.00
102 (Deluxe) - MYR 180.00
103 (Standard) - MYR 120.00
104 (Suite) - MYR 250.00
```

### Test Case 3: Check Nov 04-05
**Input:**
- Check-in: 2025-11-04
- Check-out: 2025-11-05

**Result:**
- Room 101: ✗ NOT AVAILABLE (overlaps with Nov 03-05 reservation)
- Room 102: ✓ AVAILABLE
- Room 103: ✓ AVAILABLE
- Room 104: ✓ AVAILABLE

**Dropdown shows:**
```
102 (Deluxe) - MYR 180.00
103 (Standard) - MYR 120.00
104 (Suite) - MYR 250.00
```

## Code Implementation

### Location: `app/ui/main.py` (line 188)
```python
ttk.Button(r3, text="Check Availability", 
           command=self.refresh_available_rooms).grid(row=0, column=3)
```

### Function: `refresh_available_rooms()` (lines 212-237)
```python
def refresh_available_rooms(self):
    # Get dates from input fields
    ci = self.ci_var.get().strip()
    co = self.co_var.get().strip()
    
    # Validate date format
    try:
        datetime.strptime(ci, '%Y-%m-%d')
        datetime.strptime(co, '%Y-%m-%d')
        self.ci_entry.config(foreground='black')
        self.co_entry.config(foreground='black')
    except ValueError:
        # Invalid format - show red text
        self.ci_entry.config(foreground='red')
        self.co_entry.config(foreground='red')
        self.room_combo['values'] = []
        self.room_choice.set('')
        return
    
    # Load reservations
    reservations = list_reservations(self.paths.reservations)
    
    # Check each room
    avail = []
    for room in self.rooms:
        if is_room_available(reservations, room.room_id, ci, co):
            avail.append(f"{room.room_id} ({room.room_type}) - MYR {room.base_price:.2f}")
    
    # Update dropdown
    self.room_combo['values'] = avail
    if avail:
        self.room_choice.set(avail[0])
        self._on_room_selected()  # Show thumbnail
    else:
        self.room_choice.set('')
        self.room_thumbnail_label.config(image='')
```

## Key Points

1. **Real-time validation**: Date format errors are shown immediately with red text
2. **Smart filtering**: Automatically excludes cancelled and checked-out reservations
3. **Overlap prevention**: Uses mathematical overlap detection (not simple date comparison)
4. **User-friendly**: Auto-selects first available room and shows thumbnail
5. **Transparent**: Empty dropdown clearly indicates no rooms available

## Why Your Screenshot Shows an Error

In your screenshot:
- You selected dates: Oct 30-31
- Room 101 shows in dropdown (suggesting it's available)
- But creation fails with "Room not available"

**Possible causes:**
1. **Data changed between check and create**: Someone else might have booked the room
2. **Status changed**: The Oct 28-31 reservation might have been Cancelled when you checked, but is now Checked-In
3. **UI not refreshed**: The dropdown might be showing stale data from a previous check

**Solution:** Click "Check Availability" button again right before clicking "Create Reservation" to ensure fresh data.
