"""
Quick verification script to check database status before generating graphs.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def verify_database():
    """Verify the database has clean, meaningful data."""
    
    db_path = Path(__file__).parent / "data" / "reservations.db"
    
    print("=" * 70)
    print("DATABASE VERIFICATION FOR GRAPH ANALYTICS")
    print("=" * 70)
    print()
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 1. Check total reservations
            cursor.execute("SELECT COUNT(*) FROM reservations")
            total_count = cursor.fetchone()[0]
            print(f"✓ Total Reservations: {total_count}")
            
            # 2. Check for negative stay durations
            cursor.execute("""
                SELECT COUNT(*) 
                FROM reservations 
                WHERE start_date > end_date
            """)
            negative_stays = cursor.fetchone()[0]
            
            if negative_stays > 0:
                print(f"✗ WARNING: {negative_stays} reservations with negative stay duration!")
            else:
                print(f"✓ No negative stay durations (all dates are valid)")
            
            # 3. Check date range
            cursor.execute("""
                SELECT 
                    MIN(start_date) as earliest,
                    MAX(end_date) as latest
                FROM reservations
            """)
            date_range = cursor.fetchone()
            print(f"✓ Date Range: {date_range[0]} to {date_range[1]}")
            
            # 4. Check status distribution
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM reservations 
                GROUP BY status 
                ORDER BY status
            """)
            print("\n✓ Reservation Status Distribution:")
            for row in cursor.fetchall():
                print(f"   - {row[0]}: {row[1]} reservations")
            
            # 5. Check revenue data
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    SUM(total_cost) as revenue,
                    AVG(total_cost) as avg_revenue
                FROM reservations
                WHERE status IN ('Checked-Out', 'Checked-In')
                GROUP BY status
            """)
            print("\n✓ Revenue by Status (Analytics-Ready Data):")
            total_revenue = 0
            for row in cursor.fetchall():
                total_revenue += row[2] or 0
                print(f"   - {row[0]}: {row[1]} stays, Total: RM {row[2]:.2f}, Avg: RM {row[3]:.2f}")
            print(f"   - TOTAL REVENUE: RM {total_revenue:.2f}")
            
            # 6. Check room type distribution
            cursor.execute("""
                SELECT 
                    rm.room_type,
                    COUNT(*) as stays,
                    SUM(r.total_cost) as revenue
                FROM reservations r
                JOIN rooms rm ON r.room_id = rm.room_id
                WHERE r.status IN ('Checked-Out', 'Checked-In')
                GROUP BY rm.room_type
                ORDER BY revenue DESC
            """)
            print("\n✓ Revenue by Room Type:")
            for row in cursor.fetchall():
                print(f"   - {row[0]}: {row[1]} stays, RM {row[2]:.2f}")
            
            # 7. Check monthly distribution
            cursor.execute("""
                SELECT 
                    SUBSTR(start_date, 1, 7) as month,
                    COUNT(*) as stays
                FROM reservations
                WHERE status IN ('Checked-Out', 'Checked-In')
                GROUP BY month
                ORDER BY month
            """)
            print("\n✓ Monthly Distribution (for graph analytics):")
            for row in cursor.fetchall():
                print(f"   - {row[0]}: {row[1]} stays")
            
            # 8. Data quality checks
            print("\n" + "=" * 70)
            print("DATA QUALITY CHECKS")
            print("=" * 70)
            
            # Check for zero-day stays
            cursor.execute("""
                SELECT COUNT(*) 
                FROM reservations 
                WHERE start_date = end_date
            """)
            zero_day = cursor.fetchone()[0]
            print(f"✓ Same-day check-in/out: {zero_day} reservations")
            
            # Check for missing guest info
            cursor.execute("""
                SELECT COUNT(*) 
                FROM reservations 
                WHERE guest_name = '' OR guest_phone = '' OR guest_email = ''
            """)
            missing_info = cursor.fetchone()[0]
            
            if missing_info > 0:
                print(f"⚠ Reservations with missing info: {missing_info}")
            else:
                print(f"✓ All reservations have complete guest information")
            
            # Check for cancelled reservations with revenue
            cursor.execute("""
                SELECT COUNT(*) 
                FROM reservations 
                WHERE status = 'Cancelled' AND total_cost > 0
            """)
            cancelled_with_revenue = cursor.fetchone()[0]
            
            if cancelled_with_revenue > 0:
                print(f"⚠ Cancelled reservations with revenue: {cancelled_with_revenue}")
            else:
                print(f"✓ Cancelled reservations correctly have $0 revenue")
            
            # Final assessment
            print("\n" + "=" * 70)
            print("GRAPH ANALYTICS READINESS")
            print("=" * 70)
            
            if negative_stays == 0 and cancelled_with_revenue == 0:
                print("✅ DATABASE IS READY FOR GRAPH ANALYTICS!")
                print()
                print("You can now:")
                print("  1. Launch the app: python run.py")
                print("  2. Navigate to Analytics → Revenue by Room Type")
                print("  3. Set date range: 2025-06-01 to 2025-11-30")
                print("  4. Choose 'monthly' time bucket")
                print("  5. Select 'combined' chart type")
                print("  6. Click 'Generate' to see your analytics!")
                print()
                print(f"Expected results:")
                print(f"  - 6 months of revenue trends")
                print(f"  - 3 room types compared")
                print(f"  - Total revenue: RM {total_revenue:,.2f}")
                print(f"  - Charts saved to reports/ folder")
            else:
                print("⚠ DATABASE HAS ISSUES - Run data cleanup script:")
                print("  python scripts/generate_sample_data.py")
            
            print("\n" + "=" * 70)
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        print("\nTo fix, run:")
        print("  python scripts/generate_sample_data.py")

if __name__ == "__main__":
    verify_database()
