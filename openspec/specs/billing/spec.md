# billing Specification

## Purpose
Billing logic has been consolidated into the `reservations` module. The `compute_total` function calculates stay costs with service charges and taxes.

**Note**: As of October 31, 2025, billing functionality is implemented in `app/reservations.py` rather than a separate module. This consolidation reduces module count and improves code locality since billing is exclusively used by reservation operations.

## Requirements
### Requirement: Stay Cost Calculation
The system SHALL calculate the total stay cost in MYR with service charge and tax as follows:
- subtotal = nightly_rate × number_of_nights
- service_charge = 10% of subtotal
- tax = 6% of (subtotal + service_charge)
- total = subtotal + service_charge + tax
- Rounding: round to two decimal places at final total; display two decimals

#### Scenario: Two-night stay at 100.00 MYR per night
- **WHEN** nightly_rate = 100.00 MYR and number_of_nights = 2
- **THEN** subtotal = 200.00; service_charge = 20.00; tax = 13.20; total = 233.20 MYR

### Requirement: Pricing Fields on Reservation
The system SHALL store the computed total_cost in reservations.csv for each reservation at creation and update it on modification.

#### Scenario: Persist total cost on create
- **WHEN** a reservation is created
- **THEN** the system computes total using the formula above
- **AND** persists `total_cost` in reservations.csv

