"""
Generate sample reservation data for testing graph functionality.

This script creates realistic reservation data over a 6-month period
to demonstrate revenue analytics and business insights.
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
import random
from pathlib import Path

# Room configuration (matching existing rooms.csv)
ROOMS = [
    {"room_id": 101, "room_type": "Standard", "base_price": 120.00},
    {"room_id": 102, "room_type": "Deluxe", "base_price": 180.00},
    {"room_id": 103, "room_type": "Standard", "base_price": 120.00},
    {"room_id": 104, "room_type": "Suite", "base_price": 250.00},
]

# Guest name pool for variety
GUEST_NAMES = [
    "John Smith", "Sarah Johnson", "Michael Chen", "Emily Davis",
    "David Wilson", "Lisa Anderson", "James Brown", "Maria Garcia",
    "Robert Taylor", "Jennifer Martinez", "William Lee", "Patricia White",
    "Richard Harris", "Linda Clark", "Thomas Lewis", "Barbara Walker",
    "Christopher Hall", "Elizabeth Allen", "Daniel Young", "Jessica King"
]

# Email domains
EMAIL_DOMAINS = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]

# Phone number generator
def generate_phone():
    return f"01{random.randint(0, 9)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

def generate_email(name):
    first_name = name.split()[0].lower()
    last_name = name.split()[-1].lower()
    domain = random.choice(EMAIL_DOMAINS)
    return f"{first_name}.{last_name}@{domain}"

def calculate_cost(base_price, num_nights, num_guests):
    """Calculate total cost with 16.6% tax."""
    subtotal = base_price * num_nights
    tax = subtotal * 0.166
    return round(subtotal + tax, 2)

def generate_reservations():
    """Generate 6 months of realistic reservation data."""
    reservations = []
    
    # Start from June 2025 to November 2025 (6 months)
    start_date = datetime(2025, 6, 1)
    end_date = datetime(2025, 11, 30)
    
    current_date = start_date
    
    # Generate reservations with realistic patterns
    while current_date <= end_date:
        # Weekday vs weekend probability (more bookings on weekends)
        is_weekend = current_date.weekday() >= 4  # Friday, Saturday
        
        # Higher occupancy on weekends and holidays
        if is_weekend:
            daily_bookings = random.randint(3, 4)  # 75-100% occupancy
        else:
            daily_bookings = random.randint(1, 3)  # 25-75% occupancy
        
        # Special high-demand periods (simulate holidays)
        if current_date.month == 8:  # August (summer vacation)
            daily_bookings = min(4, daily_bookings + 1)
        elif current_date.month == 10:  # October (fall break)
            daily_bookings = min(4, daily_bookings + 1)
        
        # Track which rooms are booked for this date
        available_rooms = ROOMS.copy()
        random.shuffle(available_rooms)
        
        for i in range(min(daily_bookings, len(available_rooms))):
            room = available_rooms[i]
            
            # Stay duration: mostly 1-3 nights, occasionally longer
            stay_duration = random.choices(
                [1, 2, 3, 4, 5, 7],
                weights=[30, 40, 15, 8, 5, 2],
                k=1
            )[0]
            
            check_in = current_date
            check_out = current_date + timedelta(days=stay_duration)
            
            # Skip if check_out exceeds our data range
            if check_out > end_date:
                continue
            
            # Guest count (1-4 guests, weighted toward 2)
            num_guests = random.choices([1, 2, 3, 4], weights=[25, 50, 15, 10], k=1)[0]
            
            # Guest details
            guest_name = random.choice(GUEST_NAMES)
            phone = generate_phone()
            email = generate_email(guest_name)
            
            # Calculate cost
            total_cost = calculate_cost(room["base_price"], stay_duration, num_guests)
            
            # Status: most are checked-out, some cancelled, few upcoming
            if check_out < datetime.now():
                # Past reservations: 85% checked-out, 15% cancelled
                status = random.choices(
                    ["Checked-Out", "Cancelled"],
                    weights=[85, 15],
                    k=1
                )[0]
            elif check_in <= datetime.now() < check_out:
                status = "Checked-In"
            else:
                # Future reservations: 90% confirmed, 10% cancelled
                status = random.choices(
                    ["Confirmed", "Cancelled"],
                    weights=[90, 10],
                    k=1
                )[0]
            
            # If cancelled, set cost to 0
            if status == "Cancelled":
                total_cost = 0.00
            
            # Generate reservation
            reservation = {
                "id": str(uuid.uuid4()),
                "room_id": room["room_id"],
                "guest_name": guest_name,
                "phone": phone,
                "email": email,
                "check_in_date": check_in.strftime("%Y-%m-%d"),
                "check_out_date": check_out.strftime("%Y-%m-%d"),
                "num_guests": num_guests,
                "status": status,
                "total_cost": total_cost,
                "created_at": (check_in - timedelta(days=random.randint(1, 30))).isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            reservations.append(reservation)
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return reservations

def save_to_database(reservations):
    """Save reservations to SQLite database."""
    db_path = Path(__file__).parent.parent / "data" / "reservations.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Clear existing reservations
        print(f"Clearing existing reservations...")
        cursor.execute("DELETE FROM reservations")
        conn.commit()
        print(f"Cleared {cursor.rowcount} existing reservations.")
        
        # Insert new reservations
        print(f"Inserting {len(reservations)} new reservations...")
        
        for res in reservations:
            cursor.execute("""
                INSERT INTO reservations (
                    id, room_id, guest_name, guest_phone, guest_email,
                    start_date, end_date, num_guests, status, total_cost,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                res["id"],
                res["room_id"],
                res["guest_name"],
                res["phone"],
                res["email"],
                res["check_in_date"],
                res["check_out_date"],
                res["num_guests"],
                res["status"],
                res["total_cost"],
                res["created_at"],
                res["updated_at"]
            ))
        
        conn.commit()
        print(f"Successfully inserted {len(reservations)} reservations.")
        
        # Print summary statistics
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count,
                SUM(total_cost) as total_revenue
            FROM reservations
            GROUP BY status
            ORDER BY status
        """)
        
        print("\n=== Reservation Summary ===")
        for row in cursor.fetchall():
            print(f"{row[0]}: {row[1]} reservations, Revenue: RM {row[2]:.2f}")
        
        # Monthly summary
        cursor.execute("""
            SELECT 
                SUBSTR(start_date, 1, 7) as month,
                COUNT(*) as count,
                SUM(total_cost) as revenue
            FROM reservations
            WHERE status IN ('Checked-Out', 'Checked-In')
            GROUP BY month
            ORDER BY month
        """)
        
        print("\n=== Monthly Revenue (Completed Stays Only) ===")
        for row in cursor.fetchall():
            print(f"{row[0]}: {row[1]} stays, Revenue: RM {row[2]:.2f}")
        
        # Room type performance
        cursor.execute("""
            SELECT 
                rm.room_type,
                COUNT(*) as count,
                SUM(r.total_cost) as revenue,
                AVG(r.total_cost) as avg_revenue
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.room_id
            WHERE r.status IN ('Checked-Out', 'Checked-In')
            GROUP BY rm.room_type
            ORDER BY revenue DESC
        """)
        
        print("\n=== Revenue by Room Type (Completed Stays Only) ===")
        for row in cursor.fetchall():
            print(f"{row[0]}: {row[1]} stays, Total: RM {row[2]:.2f}, Avg: RM {row[3]:.2f}")

if __name__ == "__main__":
    print("Generating sample reservation data...")
    reservations = generate_reservations()
    
    print(f"\nGenerated {len(reservations)} reservations.")
    print(f"Date range: June 2025 - November 2025 (6 months)")
    
    save_to_database(reservations)
    
    print("\n✓ Sample data generation complete!")
    print("\nThis data simulates realistic booking patterns with:")
    print("  - Higher occupancy on weekends")
    print("  - Seasonal variations (summer and fall peaks)")
    print("  - Realistic cancellation rates")
    print("  - Varied stay durations (1-7 nights)")
    print("  - Multiple room types with different price points")
    print("\nUse the analytics features to visualize:")
    print("  - Revenue trends over time")
    print("  - Room type performance comparison")
    print("  - Occupancy patterns")
    print("  - Average booking values")
