# reporting Specification

## Purpose
TBD - created by archiving change add-hotel-core-ops. Update Purpose after archive.
## Requirements
### Requirement: Daily Check-In List
The system SHALL generate an on-screen list of reservations scheduled to check in on a given date.

#### Scenario: Generate today's check-in list
- **WHEN** the user requests the check-in list for a specific date
- **THEN** the system displays all reservations with check_in_date = that date and status in {Confirmed}

### Requirement: Daily Check-Out List
The system SHALL generate an on-screen list of reservations scheduled to check out on a given date.

#### Scenario: Generate today's check-out list
- **WHEN** the user requests the check-out list for a specific date
- **THEN** the system displays all reservations with check_out_date = that date and status in {Checked-In}

### Requirement: Monthly Revenue Summary
The system SHALL compute a monthly revenue summary for a given month.

#### Scenario: Compute revenue for a month
- **WHEN** the user requests the revenue summary for YYYY-MM
- **THEN** the system sums `total_cost` for reservations whose check_out_date falls within that month
- **AND** displays the total revenue in MYR with two decimals

### Requirement: Guest Reservation Detail Report
The system SHALL generate a detailed report of guest reservations within a specified date range, showing check-in dates, check-out dates, room information, and costs per reservation.

#### Scenario: Generate report for date range
- **WHEN** the user requests a guest reservation detail report for a date range (start_date, end_date)
- **THEN** the system returns all reservations where check_in_date >= start_date AND check_in_date <= end_date
- **AND** for each reservation, displays: guest_name, room_id, check_in_date, check_out_date, total_cost
- **AND** calculates and displays the number of nights as (check_out_date - check_in_date)
- **AND** displays the total cost per reservation in MYR with two decimals

#### Scenario: Report includes grand total
- **WHEN** the guest reservation detail report is generated
- **THEN** the system computes and displays the sum of all total_cost values across the filtered reservations
- **AND** displays the grand total in MYR with two decimals

#### Scenario: Empty date range
- **WHEN** no reservations exist within the specified date range
- **THEN** the system returns an empty list and displays a grand total of MYR 0.00

