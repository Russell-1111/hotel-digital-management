# Hotel Digital Management System - User Guide

**Version 2.1**  
**Last Updated: November 17, 2025**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Daily Operations Tab](#daily-operations-tab)
3. [Reservations Tab](#reservations-tab)
4. [Availability Tab](#availability-tab)
5. [Reports Tab](#reports-tab)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)
8. [Quick Reference](#quick-reference)

---

## Getting Started

### Launching the Application

1. Double-click the application shortcut or run `python run.py` from the command line
2. The main window will open with four tabs: **Daily Ops**, **Reservations**, **Availability**, and **Reports**
3. The window is resizable (minimum 800×500 pixels) - adjust to your preferred size

### Interface Overview

The application uses a tabbed interface for different hotel management functions:

- **Daily Ops**: View today's check-ins and check-outs
- **Reservations**: Create, modify, and cancel reservations
- **Availability**: Check room availability for specific date ranges
- **Reports**: Generate revenue and guest detail reports; includes **Analytics section (Admin only)**

**Note**: Staff users will see only the Monthly Revenue Summary and Guest Reservation Details sections in the Reports tab. The Analytics section with "Revenue by Room Type" feature is restricted to administrator accounts.

---

## Daily Operations Tab

### Purpose
Quick reference for front desk staff to see which guests are checking in or out today.

### Controls

#### 1. Date Input Field
- **Location**: Top of the tab
- **Label**: "Date (YYYY-MM-DD):"
- **Function**: Set the date for which you want to view check-ins and check-outs
- **Default**: Today's date

**How to use:**
1. Click in the date field
2. Type the date in format `YYYY-MM-DD` (e.g., `2025-10-29`)
3. Click **Refresh** to update the lists

**Example 1: View today's operations**
- Date field shows today's date automatically
- Lists show current check-ins and check-outs
- No action needed unless you want a different date

**Example 2: View tomorrow's operations**
- Click the date field
- Type tomorrow's date (e.g., if today is 2025-10-29, type `2025-10-30`)
- Click **Refresh**
- Lists update to show tomorrow's check-ins and check-outs

**Error handling:**
- If you enter an invalid date format (e.g., `10/29/2025`), the date field will briefly turn red
- Re-enter the date in the correct format: `YYYY-MM-DD`

---

#### 2. Refresh Button
- **Location**: Next to the date input field
- **Function**: Updates the check-in and check-out lists based on the entered date
- **When to use**: After changing the date or when you want to see the latest data

**How to use:**
1. Optionally change the date in the date field
2. Click **Refresh**
3. Both lists update immediately

**Example:**
- You modify a reservation in the Reservations tab
- Switch back to Daily Ops
- Click **Refresh** to see the updated information

---

#### 3. Today's Check-Ins List
- **Location**: Left panel under the date controls
- **Function**: Displays all guests scheduled to check in on the selected date
- **Format**: `Room {number} | {Guest Name}`

**How to read:**
- Each line represents one reservation checking in
- Room number appears first, followed by guest name
- Empty list means no check-ins scheduled

**Example:**
```
Room 101 | Russell Hong
Room 103 | Sarah Johnson
Room 104 | Michael Chen
```

---

#### 4. Today's Check-Outs List
- **Location**: Right panel under the date controls
- **Function**: Displays all guests scheduled to check out on the selected date
- **Format**: `Room {number} | {Guest Name}`

**How to read:**
- Each line represents one reservation checking out
- Room number appears first, followed by guest name
- Empty list means no check-outs scheduled

---

## Reservations Tab

### Purpose
Create new reservations, view existing bookings, and modify or cancel reservations.

### Section 1: New Reservation Form

#### 1. Guest Name Field
- **Location**: First field in the form, top-left
- **Function**: Enter the guest's full name
- **Required**: Yes

**How to use:**
1. Click in the field
2. Type the guest's name (e.g., "Russell Hong Jian An")
3. Use full names for clarity

**Best practices:**
- Use the guest's full legal name as it appears on their ID
- Capitalize properly for professional records

---

#### 2. Phone Field
- **Location**: Middle of the first row
- **Function**: Enter the guest's contact phone number
- **Required**: Yes (for reservation confirmation)

**How to use:**
1. Type the phone number in any format (e.g., "018-383-6112" or "0183836112")
2. Include country code if international

**Example:**
- Local: `018-383-6112`
- International: `+60-18-383-6112`

---

#### 3. Email Field
- **Location**: Right side of the first row
- **Function**: Enter the guest's email address for confirmations
- **Required**: Yes

**How to use:**
1. Type the complete email address
2. Verify spelling to ensure confirmation emails are delivered

**Example:** `russellhong@gmail.com`

---

#### 4. Check-in Date Field
- **Location**: First field in the second row
- **Label**: "Check-in (YYYY-MM-DD)"
- **Function**: Set the date when the guest will arrive
- **Default**: Today's date

**How to use:**
1. Click in the field
2. Type the check-in date in format `YYYY-MM-DD`
3. Ensure the date is today or in the future

**Example 1: Same-day check-in**
- Today is 2025-10-29
- Guest checking in today
- Leave default value: `2025-10-29`

**Example 2: Future reservation**
- Today is 2025-10-29
- Guest checking in on November 5th
- Enter: `2025-11-05`

**Error handling:**
- Invalid format (e.g., `29-10-2025`) will make the field turn red
- Re-enter in correct format: `YYYY-MM-DD`

---

#### 5. Check-out Date Field
- **Location**: Middle of the second row
- **Label**: "Check-out (YYYY-MM-DD)"
- **Function**: Set the date when the guest will depart
- **Default**: Today's date (you'll usually change this)

**How to use:**
1. Type the check-out date in format `YYYY-MM-DD`
2. Must be on or after the check-in date

**Example 1: One-night stay**
- Check-in: `2025-10-29`
- Check-out: `2025-10-30`
- Guest stays one night

**Example 2: Multi-night stay**
- Check-in: `2025-10-29`
- Check-out: `2025-11-02`
- Guest stays 4 nights

**Important:**
- Same-day check-in and check-out (0 nights) is allowed but cost will be MYR 0.00
- System calculates nights automatically based on date difference

---

#### 6. Guests Field
- **Location**: Right side of the second row
- **Label**: "Guests"
- **Function**: Enter the number of guests in the party
- **Default**: 1

**How to use:**
1. Click in the field
2. Type the number of guests (must be a whole number)

**Example:**
- Solo traveler: `1`
- Couple: `2`
- Family: `4`

**Error handling:**
- Non-numeric values (e.g., "two") will show an error when creating the reservation
- Enter only numbers

---

#### 7. Available Room Dropdown
- **Location**: First field in the third row
- **Label**: "Available Room"
- **Function**: Select which room to reserve from available options
- **Format**: `{Room Number} ({Room Type}) - MYR {Price}/night`

**How to use:**
1. First, set your check-in and check-out dates
2. Click **Check Availability** button (see below)
3. Dropdown populates with available rooms
4. Click the dropdown to see all options
5. Select the desired room

**Example:**
After clicking Check Availability, you might see:
```
101 (Standard) - MYR 120.00
103 (Standard) - MYR 120.00
104 (Suite) - MYR 250.00
```

**What it means:**
- Room 101 is available, it's a Standard type, costs MYR 120.00 per night
- Room 102 is NOT in the list (already booked for these dates)

---

#### 8. Room Thumbnail Preview
- **Location**: Next to the Available Room dropdown
- **Function**: Shows a small preview image (80×60 pixels) of the selected room
- **Updates**: Automatically when you change room selection

**How it works:**
1. Select a room from the dropdown
2. Thumbnail updates instantly to show that room
3. Helps visual confirmation of room selection

**Example:**
- Select "101 (Standard) - MYR 120.00"
- Thumbnail shows image of Room 101
- Switch to "104 (Suite) - MYR 250.00"
- Thumbnail updates to show Suite image

**Note:** If no image is available, placeholder will be shown

---

#### 9. Check Availability Button ⭐
- **Location**: Third row, next to room dropdown
- **Function**: Searches for available rooms based on your entered check-in and check-out dates
- **When to use**: ALWAYS click this before selecting a room

**How to use:**
1. Enter check-in date
2. Enter check-out date
3. Click **Check Availability**
4. Dropdown populates with available rooms
5. Select your desired room
6. Click **Create Reservation**

**Example 1: Weekend booking**
- Check-in: `2025-11-01` (Friday)
- Check-out: `2025-11-03` (Sunday)
- Click **Check Availability**
- See which rooms are free for the entire weekend
- Result might show: Rooms 101, 103, 104 available; Room 102 already booked

**Example 2: Long stay**
- Check-in: `2025-11-05`
- Check-out: `2025-11-15` (10 nights)
- Click **Check Availability**
- System checks if any room is free for ALL 10 nights
- Only shows rooms available for the entire duration

**Example 3: Changing dates**
- You initially checked `2025-11-01` to `2025-11-03`
- Guest changes mind, wants `2025-11-08` to `2025-11-10`
- Update both date fields
- **MUST click Check Availability again** - old results won't be valid
- New available rooms list appears

**Common mistakes to avoid:**
- ❌ Changing dates but forgetting to click Check Availability → You'll be seeing availability for the OLD dates
- ❌ Entering invalid date formats → Button won't work until dates are corrected
- ❌ Setting check-out before check-in → No rooms will show as available

**Why this is important:**
The system must verify that your chosen room is completely free for your entire date range. A room might be available on Friday but booked on Saturday - this button ensures you only see rooms that work for the whole stay.

---

#### 10. Create Reservation Button
- **Location**: Far right of the third row
- **Function**: Creates a new reservation with all the entered information
- **When to use**: After filling all fields and selecting an available room

**Prerequisites:**
1. Guest Name filled in
2. Phone filled in
3. Email filled in
4. Check-in date entered (valid format)
5. Check-out date entered (valid format)
6. Number of guests entered (valid number)
7. Room selected from dropdown (must click Check Availability first)

**How to use:**
1. Complete all fields in the form
2. Click **Check Availability** to populate room options
3. Select a room from the dropdown
4. Click **Create Reservation**
5. System creates the reservation and refreshes all lists

**What happens:**
- Reservation is saved to the database
- Total cost is calculated automatically (nights × base price × tax multiplier)
- Room becomes unavailable for those dates
- Reservation appears in the "Existing Reservations" list below
- All fields clear, ready for next reservation
- Daily Ops lists update (if check-in/out is today)

**Example:**
```
Guest Name: Sarah Johnson
Phone: 012-345-6789
Email: sarah.j@email.com
Check-in: 2025-11-01
Check-out: 2025-11-03
Guests: 2
Available Room: 102 (Deluxe) - MYR 180.00

Click Create Reservation →
Result: Reservation created
Cost: MYR 419.76 (2 nights × MYR 180.00 × 1.166 tax)
Status: Confirmed
```

**Error scenarios:**

**Error 1: Empty required field**
- If you forget guest name, phone, or email
- Error dialog appears: "Validation Error: Please fill in all required fields"
- Fill in missing information and try again

**Error 2: No room selected**
- Error dialog: "Validation Error: Please select an available room"
- Click Check Availability and select a room

**Error 3: Invalid date**
- Error dialog: "Failed to create reservation: Invalid date format"
- Correct the date format to YYYY-MM-DD

**Error 4: Room unavailable**
- Error dialog: "Failed to create reservation: Room not available for selected dates"
- This shouldn't happen if you clicked Check Availability, but if it does:
  - Click Check Availability again to refresh
  - Select a different room

---

### Section 2: Existing Reservations List

#### 11. Reservations List
- **Location**: Large box in the middle of the tab
- **Label**: "Existing Reservations"
- **Function**: Shows all reservations in the system
- **Format**: `Room {number} | {Guest Name} | {Check-in}->{Check-out} | {Status} | MYR {Total Cost}`

**How to read:**
Each line shows complete reservation details:
- Room number
- Guest name
- Date range (arrow shows from check-in to check-out)
- Current status (Confirmed, Checked-In, Checked-Out, Cancelled)
- Total cost in Malaysian Ringgit

**Example:**
```
Room 101 | Russell Hong | 2025-10-29->2025-10-31 | Checked-In | MYR 279.84
Room 102 | Sarah Johnson | 2025-11-01->2025-11-03 | Confirmed | MYR 419.76
Room 103 | Michael Chen | 2025-10-28->2025-10-29 | Checked-Out | MYR 139.92
Room 104 | Emma Wilson | 2025-10-30->2025-10-31 | Cancelled | MYR 291.50
```

**Status meanings:**
- **Confirmed**: Future reservation, not yet checked in
- **Checked-In**: Guest is currently staying (check-in date has passed)
- **Checked-Out**: Stay completed (check-out date has passed)
- **Cancelled**: Reservation was cancelled

**Selecting a reservation:**
1. Click on any line to select it (it will highlight)
2. Use Modify or Cancel buttons (see below)

---

#### 12. Refresh Button (Reservations List)
- **Location**: Below the reservations list, far left
- **Function**: Reloads the reservation list from the database
- **When to use**: To see the latest reservations if you suspect data has changed

**How to use:**
1. Click **Refresh**
2. List updates with current data

**Example:**
- Another staff member creates a reservation on a different computer
- Click Refresh to see their new reservation in your list

**Note:** Most operations (Create, Modify, Cancel) automatically refresh the list, so manual refresh is rarely needed.

---

#### 13. Modify Selected Button
- **Location**: Below the reservations list, center
- **Function**: Opens a dialog to change details of an existing reservation
- **Restrictions**: Cannot modify Cancelled or Checked-Out reservations

**How to use:**
1. Click on a reservation in the list to select it
2. Click **Modify Selected**
3. A new window opens with pre-filled information
4. Change any details you need
5. Click **Save Changes** in the dialog

**What you can modify:**
- Guest Name
- Phone
- Email
- Check-in date (if changing dates, use Refresh Rooms button)
- Check-out date
- Number of guests
- Room (if changing dates or switching rooms)

**Example 1: Change guest contact info**
- Guest's phone number changed
- Select the reservation
- Click **Modify Selected**
- Update the Phone field
- Click **Save Changes**

**Example 2: Extend stay**
- Original: Check-out on 2025-11-03
- Guest wants to stay until 2025-11-05
- Select the reservation
- Click **Modify Selected**
- Change check-out date to `2025-11-05`
- Click **Refresh Rooms** (ensures room is available for extra nights)
- Confirm room is still selected
- Click **Save Changes**
- Total cost automatically recalculates

**Example 3: Change room**
- Guest wants to upgrade from Standard to Suite
- Select the reservation
- Click **Modify Selected**
- Click **Refresh Rooms** button in the dialog
- Select the new room from dropdown (e.g., "104 (Suite) - MYR 250.00")
- Click **Save Changes**
- Old room becomes available, new room becomes booked

**Example 4: Complex modification - change dates AND room**
- Original: Room 101, Nov 1-3
- New: Room 104, Nov 5-7
- Select the reservation
- Click **Modify Selected**
- Update check-in to `2025-11-05`
- Update check-out to `2025-11-07`
- Click **Refresh Rooms** (critical step!)
- Select new room: "104 (Suite) - MYR 250.00"
- Click **Save Changes**

**Error scenarios:**

**Error 1: No reservation selected**
- Nothing happens when you click the button
- Click on a reservation line first to select it

**Error 2: Cancelled or Checked-Out reservation**
- Dialog opens but you shouldn't modify these
- System may prevent saving or show error

**Error 3: Room not available for new dates**
- You change dates but forget to click Refresh Rooms
- Error when saving: "Room not available for selected dates"
- Click Refresh Rooms in the dialog
- Select an available room

**Critical tip:**
When changing dates, ALWAYS click the **Refresh Rooms** button in the modification dialog before saving. This ensures the system checks availability for your new date range.

---

#### 14. Cancel Selected Button
- **Location**: Below the reservations list, right side
- **Function**: Cancels a reservation (sets status to "Cancelled")
- **When to use**: When a guest cancels their booking

**How to use:**
1. Click on a reservation in the list to select it
2. Click **Cancel Selected**
3. Reservation status changes to "Cancelled"
4. Room becomes available for those dates again
5. List refreshes automatically

**Example:**
```
Before:
Room 102 | Sarah Johnson | 2025-11-01->2025-11-03 | Confirmed | MYR 419.76

After cancellation:
Room 102 | Sarah Johnson | 2025-11-01->2025-11-03 | Cancelled | MYR 419.76
```

**What happens:**
- Reservation remains in the system (for records) but marked as Cancelled
- Room 102 becomes available again for Nov 1-3
- Other staff can now book that room for those dates
- Reservation still appears in lists (filtered appropriately in reports)

**Important notes:**
- Cancellation is immediate - no confirmation dialog
- Cannot undo a cancellation through the UI (would need to create a new reservation)
- Cancelled reservations cannot be modified (status is final)

**Error scenario:**
- If no reservation is selected, nothing happens
- Select a reservation first, then click Cancel Selected

---

## Availability Tab

### Purpose
Visually check which rooms are available or booked for a specific date range. Includes room images and pricing.

### Controls

#### 15. Start Date Field
- **Location**: Top-left of the tab
- **Label**: "Start (YYYY-MM-DD)"
- **Function**: Set the beginning of the date range to check
- **Default**: Today's date

**How to use:**
1. Click in the field
2. Type the start date in format `YYYY-MM-DD`
3. Click **Check** button

---

#### 16. End Date Field
- **Location**: Top, middle
- **Label**: "End (YYYY-MM-DD)"
- **Function**: Set the end of the date range to check
- **Default**: Today's date

**How to use:**
1. Type the end date in format `YYYY-MM-DD`
2. Must be on or after the start date
3. Click **Check** button

---

#### 17. Check Button (Availability)
- **Location**: Top-right, next to date fields
- **Function**: Searches for room availability across all rooms for the specified date range
- **When to use**: After entering start and end dates

**How to use:**
1. Enter Start date
2. Enter End date
3. Click **Check**
4. Room list updates with availability status

**Example 1: Check weekend availability**
- Start: `2025-11-01` (Friday)
- End: `2025-11-03` (Sunday)
- Click **Check**
- See all four rooms with their status:
  - Room 101: Available (green)
  - Room 102: Unavailable (red)
  - Room 103: Available (green)
  - Room 104: Available (green)

**Example 2: Check availability for a specific date**
- Start: `2025-11-05`
- End: `2025-11-05` (same day)
- Click **Check**
- See which rooms are free on just that one day

**Example 3: Long-term availability**
- Start: `2025-11-01`
- End: `2025-11-30` (entire month)
- Click **Check**
- Shows which rooms are available for the ENTIRE month
- A room is only "Available" if it's free for ALL 30 days

---

#### 18. Room Availability Display List
- **Location**: Main area below the check button
- **Function**: Shows each room with preview image, details, and availability status
- **Scrollable**: Yes (if list is long)

**Display format for each room:**
```
[Room Image Preview 320×240]  Room 101 (Standard)
                              Status: Available (green) or Unavailable (red)
                              Price: MYR 120.00/night
─────────────────────────────────────────────────────────────────
[Room Image Preview 320×240]  Room 102 (Deluxe)
                              Status: Unavailable (red)
                              Price: MYR 180.00/night
```

**How to read:**
- **Green "Available"**: Room is free for the entire date range
- **Red "Unavailable"**: Room has at least one booking during the date range
- Room image gives visual confirmation of room type
- Price shown is per-night base price

**Example interpretation:**

**Scenario:** You checked Nov 1-3:
```
Room 101 (Standard) - Available - MYR 120.00/night
  → Can be booked for all of Nov 1, 2, and checkout Nov 3

Room 102 (Deluxe) - Unavailable - MYR 180.00/night
  → Has a booking on at least one of those nights (Nov 1, 2, or 3)

Room 103 (Standard) - Available - MYR 120.00/night
  → Can be booked for all of Nov 1, 2, and checkout Nov 3

Room 104 (Suite) - Available - MYR 250.00/night
  → Can be booked for all of Nov 1, 2, and checkout Nov 3
```

**Use cases:**

**Use case 1: Quick visual scan**
- Guest calls asking "Do you have anything available this weekend?"
- Switch to Availability tab
- Enter weekend dates
- Click Check
- Scan the list - any green means yes
- Tell guest: "We have Room 101, 103, and 104 available"

**Use case 2: Compare room options**
- Guest wants to see room types and prices
- Use the preview images to show different room styles
- Compare Standard (MYR 120) vs Deluxe (MYR 180) vs Suite (MYR 250)
- Help guest make a decision

**Use case 3: Planning ahead**
- Check holiday weekend availability in advance
- Enter dates a month out
- See which rooms are already booking up
- Identify high-demand periods

---

## Reports Tab

### Purpose
Generate financial reports and guest detail summaries for management and accounting.

### Section 1: Monthly Revenue Summary

#### 19. Month Input Field
- **Location**: Top section, "Monthly Revenue Summary"
- **Label**: "Month (YYYY-MM):"
- **Function**: Enter the month for which you want to calculate revenue
- **Default**: Current month
- **Format**: Year and month only (e.g., `2025-10`)

**How to use:**
1. Click in the field
2. Type the month in format `YYYY-MM`
3. Click **Compute Revenue**

**Examples:**
- October 2025: `2025-10`
- December 2024: `2024-12`
- January 2026: `2026-01`

---

#### 20. Compute Revenue Button
- **Location**: Next to the month input field
- **Function**: Calculates total revenue from all reservations in the specified month
- **When to use**: Monthly financial reporting, accounting

**How to use:**
1. Enter the month (or use default current month)
2. Click **Compute Revenue**
3. Result appears below

**What it calculates:**
- Sums the `total_cost` of all reservations with check-in dates in that month
- Includes Confirmed, Checked-In, and Checked-Out reservations
- Excludes Cancelled reservations
- Shows result in Malaysian Ringgit with 2 decimal places

**Example 1: Current month**
- Today is October 29, 2025
- Field shows `2025-10`
- Click **Compute Revenue**
- Result: `MYR 2,450.88`
- This is total revenue from all October check-ins

**Example 2: Previous month**
- Want to see September revenue
- Change field to `2025-09`
- Click **Compute Revenue**
- Result shows September's total

**Example 3: Year-end reporting**
- December wrap-up
- Month: `2025-12`
- Click **Compute Revenue**
- Get December revenue for annual report

---

#### 21. Revenue Display
- **Location**: Large text below the Compute Revenue button
- **Function**: Shows the calculated total revenue
- **Format**: `MYR {amount}` in large bold text
- **Default**: `MYR 0.00`

**How to read:**
- Amount shown is the total of all qualifying reservations in the selected month
- Updated each time you click Compute Revenue
- Formatted to 2 decimal places

---

### Section 2: Guest Reservation Details

#### 22. Start Date Field (Report)
- **Location**: "Guest Reservation Details" section, left
- **Label**: "Start Date (YYYY-MM-DD):"
- **Function**: Set the beginning date for the report range
- **Default**: First day of current month
- **Format**: `YYYY-MM-DD`

**How to use:**
1. Type the start date for your report
2. Click **Generate Report**

**Example:**
- Want to see all October reservations
- Start Date: `2025-10-01`
- End Date: `2025-10-31`

---

#### 23. End Date Field (Report)
- **Location**: "Guest Reservation Details" section, middle
- **Label**: "End Date (YYYY-MM-DD):"
- **Function**: Set the ending date for the report range
- **Default**: Today's date
- **Format**: `YYYY-MM-DD`

**How to use:**
1. Type the end date for your report
2. Click **Generate Report**

---

#### 24. Generate Report Button
- **Location**: Right side of the date range inputs
- **Function**: Creates a detailed table of all reservations within the specified date range
- **When to use**: Reviewing guest stays, creating detailed financial reports, auditing

**How to use:**
1. Set Start Date
2. Set End Date
3. Click **Generate Report**
4. Table populates with matching reservations

**What it shows:**
A table with these columns:
- **Guest Name**: Full name from reservation
- **Room ID**: Which room they stayed in
- **Check-In**: Check-in date
- **Check-Out**: Check-out date
- **Nights**: Number of nights stayed (auto-calculated)
- **Total Cost (MYR)**: Total cost of the reservation

**Example 1: Monthly guest report**
- Start: `2025-10-01`
- End: `2025-10-31`
- Click **Generate Report**

Result table:
```
Guest Name          Room  Check-In    Check-Out   Nights  Total Cost
──────────────────────────────────────────────────────────────────────
Russell Hong        101   2025-10-29  2025-10-31  2       MYR 279.84
Sarah Johnson       102   2025-10-01  2025-10-03  2       MYR 419.76
Michael Chen        103   2025-10-15  2025-10-16  1       MYR 139.92
Emma Wilson         104   2025-10-20  2025-10-22  2       MYR 583.00

Grand Total: MYR 1,422.52
```

**Example 2: Weekly audit**
- Start: `2025-10-23`
- End: `2025-10-29`
- Click **Generate Report**
- See only reservations that checked in during that week

**Example 3: Single-day report**
- Start: `2025-10-29`
- End: `2025-10-29`
- Click **Generate Report**
- See all reservations with check-in on exactly that date

**Filtering behavior:**
- Report includes reservations where check-in date falls within the range
- Excludes Cancelled reservations
- Sorted by check-in date (earliest first)

---

#### 25. Guest Details Table
- **Location**: Main area of the Guest Reservation Details section
- **Function**: Displays the generated report in table format
- **Scrollable**: Yes (vertical scrollbar if many reservations)

**Columns explained:**

1. **Guest Name**: Helps identify who stayed
2. **Room ID**: Which room they occupied
3. **Check-In**: Arrival date
4. **Check-Out**: Departure date
5. **Nights**: Automatically calculated (Check-Out date minus Check-In date)
   - Same-day check-in/out = 0 nights
   - One-night stay: Check-out next day = 1 night
6. **Total Cost (MYR)**: Full cost including tax

**Sorting:**
- Rows are ordered by check-in date (ascending)
- Earliest check-in appears at the top

**Selecting rows:**
- Click on any row to highlight it
- Useful for reviewing specific entries
- No action buttons (view-only table)

---

#### 26. Grand Total Display
- **Location**: Bottom of the Guest Reservation Details section
- **Label**: "Grand Total:"
- **Function**: Shows the sum of all Total Cost values in the table
- **Format**: Large bold text, `MYR {amount}`

**How to read:**
- Automatically updates when you generate a report
- Sum of all reservations shown in the table
- Shows `MYR 0.00` if no reservations match the date range

**Example:**
If your report shows 10 reservations with costs ranging from MYR 139.92 to MYR 583.00:
```
Grand Total: MYR 3,847.20
```

**Use cases:**
- **Accounting**: Daily, weekly, or monthly revenue verification
- **Management**: Track booking trends and revenue patterns
- **Auditing**: Cross-reference with bank deposits and payment records

---

### Section 3: Revenue Analytics by Room Type (ADMIN ONLY)

**Access Control**: This feature is restricted to users with administrator privileges. Staff users cannot access revenue analytics.

#### 27. Revenue by Room Type Button
- **Location**: Analytics section in Reports tab or Analytics menu
- **Function**: Opens the Revenue Analytics dialog
- **Access**: Admin only
- **When to use**: Analyzing revenue trends, identifying top-performing room types, making pricing decisions

**How to use:**
1. Click **"Revenue by Room Type"** button
2. Analytics dialog opens with configuration options

---

#### 28. Analytics Dialog - Date Range Selection

**Start Date Field**
- **Label**: "Start Date (YYYY-MM-DD):"
- **Function**: Set the beginning of the analysis period
- **Format**: `YYYY-MM-DD`

**End Date Field**
- **Label**: "End Date (YYYY-MM-DD):"
- **Function**: Set the end of the analysis period
- **Format**: `YYYY-MM-DD`

**How to use:**
1. Enter start date (e.g., `2025-11-01`)
2. Enter end date (e.g., `2025-11-30`)
3. Select time bucket and chart type
4. Click **Generate**

**Example 1: Monthly analysis**
- Start: `2025-11-01`
- End: `2025-11-30`
- Bucket: Monthly
- Shows revenue by room type for November

**Example 2: Quarterly trend**
- Start: `2025-09-01`
- End: `2025-11-30`
- Bucket: Monthly
- Chart Type: Trend
- Shows 3-month revenue trends by room type

---

#### 29. Time Bucket Selection
- **Location**: Middle section of Analytics dialog
- **Label**: "Time Bucket:"
- **Function**: Choose how to group the data
- **Options**: 
  - **Daily**: Group by individual days
  - **Weekly**: Group by week (Sunday to Saturday)
  - **Monthly**: Group by month (YYYY-MM)
  - **Quarterly**: Group by quarter (YYYY-Q1/Q2/Q3/Q4)

**How to use:**
1. Select radio button for desired bucket
2. Affects how data is aggregated and displayed

**Example 1: Daily bucket**
- Best for short-term analysis (1-2 weeks)
- Shows day-by-day revenue patterns
- Useful for identifying busy days

**Example 2: Monthly bucket**
- Best for long-term trends (3-12 months)
- Shows month-over-month growth
- Standard for financial reporting

**Example 3: Quarterly bucket**
- Best for annual/seasonal analysis
- Shows quarter performance
- Useful for strategic planning

---

#### 30. Chart Type Selection
- **Location**: Bottom section of Analytics dialog
- **Label**: "Chart Type:"
- **Function**: Choose visualization style
- **Options**:
  - **Trend**: Line chart showing trends over time
  - **Bar**: Bar chart showing absolute values
  - **Combined**: Both trend and bar charts side-by-side

**How to use:**
1. Select radio button for desired chart type
2. Click **Generate** to create visualization

**Chart Type Guide:**

**Trend (Line Chart)**
- Shows changes over time
- Each room type has a colored line
- Best for: Identifying patterns, seasonal trends, growth/decline
- Use when: Analyzing time-based changes

**Bar (Bar Chart)**
- Shows absolute values for comparison
- Each time period has grouped bars by room type
- Best for: Comparing room types, seeing exact values
- Use when: Making pricing decisions, capacity planning

**Combined**
- Shows both trend and bar charts
- Comprehensive view
- Best for: Full analysis, presentations, reports
- Use when: Need both perspective and detail

---

#### 31. Generate Button
- **Location**: Bottom-right of Analytics dialog
- **Function**: Creates charts and exports files
- **When to use**: After configuring date range, time bucket, and chart type

**How to use:**
1. Configure all settings
2. Click **Generate**
3. System processes data and creates visualizations
4. Success dialog shows file paths
5. Files saved to `reports/` directory

**What happens:**
- SQL aggregation runs on reservations data
- Revenue calculated by room type and time period
- Chart(s) generated using matplotlib
- PNG file saved with timestamp
- CSV file saved with same timestamp
- Success message displays file paths

**File naming convention:**
```
revenue_by_room_type_{bucket}_{start}_{end}_{timestamp}.png
revenue_by_room_type_{bucket}_{start}_{end}_{timestamp}.csv
```

**Example:**
```
Configuration:
- Start: 2025-11-01
- End: 2025-11-30
- Bucket: Monthly
- Chart: Combined
- Generated: 2025-11-17 14:30:45

Files created:
reports/revenue_by_room_type_monthly_2025-11-01_2025-11-30_20251117_143045.png
reports/revenue_by_room_type_monthly_2025-11-01_2025-11-30_20251117_143045.csv
```

---

#### 32. Exported PNG Chart
- **Location**: `reports/` directory
- **Format**: PNG image (1200×800 pixels, 100 DPI)
- **Content**: Professional chart with:
  - Title showing date range
  - Legend identifying room types
  - Axis labels with dates and revenue (MYR)
  - Grid for readability
  - Color-coded room types

**How to use:**
1. Navigate to `reports/` folder
2. Open PNG file with image viewer
3. Use in presentations, reports, or emails
4. Print for meetings

---

#### 33. Exported CSV Data
- **Location**: `reports/` directory
- **Format**: CSV (comma-separated values)
- **Columns**: 
  - `time_bucket`: Date/period identifier
  - `room_type`: Room type name
  - `total_revenue`: Revenue in MYR
  - `reservation_count`: Number of reservations

**How to use:**
1. Open with Excel or any spreadsheet software
2. Perform custom analysis
3. Create pivot tables
4. Import into accounting software
5. Share with stakeholders

**Example CSV content:**
```csv
time_bucket,room_type,total_revenue,reservation_count
2025-11,Standard,3600.00,12
2025-11,Deluxe,5400.00,10
2025-11,Suite,7500.00,6
```

---

### Analytics Use Cases

**Use Case 1: Identify best-performing room type**
1. Open Analytics dialog
2. Set last 3 months date range
3. Bucket: Monthly
4. Chart: Bar
5. Generate
6. Compare bar heights to see which room type generates most revenue

**Use Case 2: Track seasonal trends**
1. Set 12-month date range (full year)
2. Bucket: Monthly
3. Chart: Trend
4. Generate
5. Look for peaks and valleys across different room types
6. Plan pricing and promotions accordingly

**Use Case 3: Quarterly business review**
1. Set date range for completed quarter
2. Bucket: Quarterly
3. Chart: Combined
4. Generate
5. Export CSV for detailed analysis
6. Use PNG in presentation

**Use Case 4: Week-by-week performance**
1. Set 8-week date range
2. Bucket: Weekly
3. Chart: Trend
4. Generate
5. Identify which weeks have highest/lowest revenue
6. Adjust staffing and inventory

---

## Common Workflows

### Workflow 1: Walk-in Guest (Same-Day Reservation)

**Scenario:** Guest arrives without reservation and wants a room for tonight.

1. Switch to **Reservations** tab
2. Fill in guest information:
   - Guest Name, Phone, Email
3. Check-in date: Use today's date (pre-filled)
4. Check-out date: Enter tomorrow's date
5. Number of guests: Enter count
6. Click **Check Availability**
7. Select an available room from the dropdown
8. Click **Create Reservation**
9. Done! Guest is checked in

**Time estimate:** 2-3 minutes

---

### Workflow 2: Phone Reservation for Future Date

**Scenario:** Guest calls to book a room for next month.

1. Switch to **Reservations** tab
2. Collect guest information over the phone:
   - Full name, phone number, email
3. Ask for desired dates
4. Enter check-in and check-out dates
5. Click **Check Availability**
6. Read available room options to guest (Standard MYR 120, Deluxe MYR 180, Suite MYR 250)
7. Guest selects room type
8. Select that room from dropdown
9. View the thumbnail to confirm room appearance
10. Click **Create Reservation**
11. Confirm total cost to guest
12. Provide confirmation (guest name + room number + dates)

**Time estimate:** 3-5 minutes

---

### Workflow 3: Guest Wants to Extend Stay

**Scenario:** Currently checked-in guest wants to stay extra nights.

1. Switch to **Reservations** tab
2. Find guest's reservation in the Existing Reservations list
3. Click on their reservation to select it
4. Click **Modify Selected**
5. In the dialog, change the check-out date to later date
6. Click **Refresh Rooms** button
7. Confirm their current room is still available
8. Click **Save Changes**
9. Note the new total cost
10. Inform guest of additional charges

**Time estimate:** 2 minutes

---

### Workflow 4: Morning Front Desk Setup

**Scenario:** Start of shift, review today's operations.

1. Launch application
2. **Daily Ops** tab opens by default
3. Review "Today's Check-Ins" list
   - Prepare rooms listed
   - Note guest names for arrival
4. Review "Today's Check-Outs" list
   - Prepare final bills
   - Schedule room cleaning
5. Switch to **Availability** tab
6. Keep start/end as today's date
7. Click **Check**
8. Note which rooms are available for walk-ins

**Time estimate:** 5 minutes

---

### Workflow 5: End-of-Month Financial Report

**Scenario:** Generate revenue report for accounting department.

1. Switch to **Reports** tab
2. **Monthly Revenue Summary** section:
   - Month field shows current month
   - Click **Compute Revenue**
   - Note the total (e.g., MYR 15,234.56)
3. **Guest Reservation Details** section:
   - Start Date: First day of month (e.g., `2025-10-01`)
   - End Date: Last day of month (e.g., `2025-10-31`)
   - Click **Generate Report**
4. Review table for accuracy
5. Note Grand Total matches Monthly Revenue
6. Export or print if needed (screenshot or external tool)

**Time estimate:** 3 minutes

---

### Workflow 6: Check Availability for Group Booking

**Scenario:** Corporate client needs 3 rooms for the same dates.

1. Switch to **Availability** tab
2. Enter the group's start date
3. Enter the group's end date
4. Click **Check**
5. Count how many rooms show "Available" (green)
6. If 3+ rooms available:
   - Switch to **Reservations** tab
   - Create first reservation with these dates
   - Click **Check Availability** (refreshes after first booking)
   - Create second reservation
   - Repeat for third
7. If fewer than 3 rooms available:
   - Inform client of limited availability
   - Offer alternative dates

**Time estimate:** 5-10 minutes for 3 rooms

---

## Troubleshooting

### Problem: Date field turns red when I type a date

**Cause:** Invalid date format

**Solution:**
- Use format `YYYY-MM-DD` exactly
- Examples: `2025-10-29`, `2025-12-01`, `2026-01-15`
- NOT: `10/29/2025`, `29-10-2025`, `Oct 29 2025`
- Year must be 4 digits, month and day must be 2 digits

---

### Problem: "Check Availability" button shows no rooms

**Causes:**
1. Invalid dates (fix date format first)
2. All rooms genuinely booked for those dates
3. Check-out date is before or same as check-in date (0-night stays may show all rooms unavailable in some contexts)

**Solutions:**
1. Verify date formats are correct (`YYYY-MM-DD`)
2. Try different dates
3. Check Availability tab to visually confirm room statuses
4. Ensure check-out is after check-in for normal stays

---

### Problem: Cannot modify or cancel a reservation

**Causes:**
1. No reservation selected
2. Reservation status is already "Cancelled" or "Checked-Out"

**Solutions:**
1. Click on the reservation in the list to select it (should highlight)
2. Check status - if Cancelled or Checked-Out, modification is not allowed
3. For cancelled reservations, create a new one instead

---

### Problem: Error dialog appears: "Check C:\...\logs\app.log for details"

**Cause:** Unexpected system error

**Solution:**
1. Note the error message
2. Try the operation again
3. If error persists:
   - Navigate to the logs folder in your installation directory
   - Open `app.log` with a text editor
   - Look for recent error entries (timestamped)
   - Contact IT support with error details

---

### Problem: Room thumbnail doesn't appear

**Causes:**
1. Room image file missing
2. Image path incorrect in system

**Solution:**
- This doesn't affect functionality - reservation can still be created
- Contact IT to update room images
- Use room number and type to identify room instead

---

### Problem: Grand Total doesn't match Monthly Revenue

**Causes:**
1. Different date ranges being compared
2. Monthly Revenue uses check-in month; Guest Details uses date range

**Solution:**
- Ensure Guest Details date range covers the entire month (1st to last day)
- Ensure month in Monthly Revenue matches the Guest Details range
- Example:
  - Monthly Revenue: `2025-10`
  - Guest Details: Start `2025-10-01`, End `2025-10-31`
  - Both should then match

---

### Problem: "Refresh Rooms" in modify dialog shows no rooms

**Cause:** New dates conflict with existing bookings

**Solution:**
1. Try different dates
2. Or choose a different room that's available
3. Check Availability tab to see which rooms are free for new dates
4. May need to split the stay across different rooms if extending significantly

---

### Problem: Application window is too small or too large

**Solution:**
- Click and drag window edges to resize
- Minimum size: 800×500 pixels
- Resize to your preferred size - setting persists for session
- Content areas will expand to fill available space

---

## Quick Reference

### Date Format
**Always use:** `YYYY-MM-DD`
- ✅ `2025-10-29`
- ✅ `2025-12-01`
- ❌ `10/29/2025`
- ❌ `29-10-2025`

### Reservation Status Flow
1. **Confirmed** → Newly created, check-in date in future
2. **Checked-In** → Check-in date has passed, stay in progress
3. **Checked-Out** → Check-out date has passed, stay completed
4. **Cancelled** → Reservation cancelled

### Tab Navigation
- **F1** (or Click): Daily Ops
- **F2** (or Click): Reservations
- **F3** (or Click): Availability
- **F4** (or Click): Reports (includes Analytics section)

### Room Types and Base Prices
- **Standard** (101, 103): MYR 120.00/night
- **Deluxe** (102): MYR 180.00/night
- **Suite** (104): MYR 250.00/night

*Note: Total cost includes tax multiplier (16.6%), so final price will be higher than base price × nights*

### Critical Reminders

⚠️ **Always click "Check Availability"** before creating a reservation or after changing dates

⚠️ **In Modify dialog, click "Refresh Rooms"** whenever you change check-in or check-out dates

⚠️ **Date format matters** - use YYYY-MM-DD everywhere

⚠️ **Selected room is required** - dropdown must have a room chosen before creating reservation

---

## Support

For technical issues or questions not covered in this guide:

1. Check the `logs/app.log` file for error details
2. Contact your IT support team
3. Reference this guide's section related to your issue

**Version:** 2.1  
**Last Updated:** November 17, 2025

---

*This guide covers all UI functions as of the current system version. Features and workflows may be updated in future releases.*
