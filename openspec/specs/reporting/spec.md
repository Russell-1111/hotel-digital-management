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

