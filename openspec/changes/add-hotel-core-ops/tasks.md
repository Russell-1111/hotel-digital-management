## 1. Implementation
- [x] 1.1 Define CSV schemas
  - rooms.csv: room_id,room_type,base_price
  - reservations.csv: reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at
- [x] 1.2 Storage module
  - [x] Read/write CSV with file locking
  - [x] Configurable data directory; create if missing
  - [x] Backup scheduler at 02:30; retain 7 days; timestamped files under backups/
- [x] 1.3 Rooms module
  - [x] Load inventory from rooms.csv
  - [x] Derive status (Available/Reserved/Occupied) from reservations + current time
- [x] 1.4 Reservations module
  - [x] Availability check across dates (prevent double-booking)
  - [x] Create reservation (same-day supported); assign room and set status Confirmed
  - [x] Modify reservation with validation; cancel reservation (free room)
  - [x] Automatic status transitions at check-in/out times
- [x] 1.5 Billing module
  - [x] Compute subtotal = nightly_rate * nights
  - [x] Service charge = 10% of subtotal
  - [x] Tax = 6% of (subtotal + service charge)
  - [x] Total = subtotal + service charge + tax (MYR, 2 decimals)
- [x] 1.6 Reporting module
  - [x] Daily check-in list + check-out list (on-screen)
  - [x] Monthly revenue summary (sum of totals for stays completed in month)
- [x] 1.7 UI (Tkinter)
  - [x] Reservations screen (create/modify/cancel)
  - [x] Availability view (by date range)
  - [x] Daily ops dashboard (today's check-ins/outs)
  - [x] Reports viewer (monthly revenue)

## 2. Testing
- [x] 2.1 Pytest setup and fixtures (temp dirs for CSV/backup)
- [x] 2.2 Unit tests: billing calculations, date/status transitions, CSV I/O
- [x] 2.3 Integration: reservation flow + backups
- [x] 2.4 Coverage ≥ 70% across billing and reservations modules

## 3. Documentation
- [x] 3.1 Update project.md if conventions change
- [x] 3.2 Add sample CSVs and README usage notes
