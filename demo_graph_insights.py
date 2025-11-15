"""
Demonstration script showing how graph analytics provide business insights.

This script generates various analytics reports and visualizations to help
hotel management understand revenue patterns and make data-driven decisions.
"""

from pathlib import Path
from datetime import datetime
from app.analytics import aggregate_revenue_by_room_type
from app.visualization import generate_and_export_analytics

def main():
    """Generate analytics demonstrating business insights."""
    
    db_path = Path("data/reservations.db")
    output_dir = Path("reports")
    
    print("=" * 70)
    print("HOTEL REVENUE ANALYTICS - Business Insights Demo")
    print("=" * 70)
    print()
    
    # Analysis period: 6 months of data
    start_date = "2025-06-01"
    end_date = "2025-11-30"
    
    print(f"Analysis Period: {start_date} to {end_date}")
    print()
    
    # 1. Monthly Revenue Trends
    print("\n" + "=" * 70)
    print("1. MONTHLY REVENUE TRENDS")
    print("=" * 70)
    print("\nBusiness Question: How is our revenue trending month over month?")
    print("Actionable Insights:")
    print("  • Identify peak and slow seasons")
    print("  • Plan staffing and inventory accordingly")
    print("  • Set dynamic pricing strategies")
    print()
    
    monthly_df = aggregate_revenue_by_room_type(
        db_path=db_path,
        start_date=start_date,
        end_date=end_date,
        time_bucket="monthly"
    )
    
    print("Monthly Revenue by Room Type:")
    print(monthly_df.to_string(index=False))
    print()
    
    # Generate monthly trend chart
    png_path, csv_path = generate_and_export_analytics(
        df=monthly_df,
        chart_type="combined",
        output_dir=output_dir,
        time_bucket="monthly",
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"✓ Monthly trend chart saved: {png_path}")
    print(f"✓ Data exported to: {csv_path}")
    
    # Calculate insights
    total_by_month = monthly_df.groupby('time_bucket')['total_revenue'].sum()
    peak_month = total_by_month.idxmax()
    peak_revenue = total_by_month.max()
    slowest_month = total_by_month.idxmin()
    slowest_revenue = total_by_month.min()
    
    print(f"\n📊 Key Insights:")
    print(f"   Peak Month: {peak_month} (RM {peak_revenue:,.2f})")
    print(f"   Slowest Month: {slowest_month} (RM {slowest_revenue:,.2f})")
    print(f"   Revenue Variation: {((peak_revenue - slowest_revenue) / slowest_revenue * 100):.1f}%")
    
    # 2. Room Type Performance
    print("\n" + "=" * 70)
    print("2. ROOM TYPE PERFORMANCE COMPARISON")
    print("=" * 70)
    print("\nBusiness Question: Which room types generate the most revenue?")
    print("Actionable Insights:")
    print("  • Optimize room mix and allocation")
    print("  • Focus marketing on high-performing categories")
    print("  • Identify underperforming segments for improvement")
    print()
    
    # Aggregate by room type
    room_performance = monthly_df.groupby('room_type').agg({
        'total_revenue': 'sum',
        'reservation_count': 'sum',
        'avg_cost_per_reservation': 'mean'
    }).round(2)
    
    room_performance = room_performance.sort_values('total_revenue', ascending=False)
    
    print("Overall Room Type Performance:")
    print(room_performance.to_string())
    print()
    
    print(f"📊 Key Insights:")
    for idx, (room_type, row) in enumerate(room_performance.iterrows(), 1):
        revenue = row['total_revenue']
        count = row['reservation_count']
        avg = row['avg_cost_per_reservation']
        total_revenue = room_performance['total_revenue'].sum()
        market_share = (revenue / total_revenue * 100)
        
        print(f"   {idx}. {room_type}:")
        print(f"      Revenue: RM {revenue:,.2f} ({market_share:.1f}% of total)")
        print(f"      Bookings: {int(count)}")
        print(f"      Avg Value: RM {avg:.2f} per reservation")
    
    # 3. Weekly Patterns (for operational planning)
    print("\n" + "=" * 70)
    print("3. WEEKLY BOOKING PATTERNS")
    print("=" * 70)
    print("\nBusiness Question: Are there weekly patterns we should know about?")
    print("Actionable Insights:")
    print("  • Staff scheduling optimization")
    print("  • Weekend vs weekday pricing strategies")
    print("  • Promotional campaign timing")
    print()
    
    weekly_df = aggregate_revenue_by_room_type(
        db_path=db_path,
        start_date=start_date,
        end_date=end_date,
        time_bucket="weekly"
    )
    
    # Show sample of weekly data
    print("Sample Weekly Revenue (first 10 weeks):")
    print(weekly_df.head(10).to_string(index=False))
    print(f"... ({len(weekly_df)} total weekly records)")
    print()
    
    # Generate weekly trend chart
    png_path_weekly, csv_path_weekly = generate_and_export_analytics(
        df=weekly_df,
        chart_type="trend",
        output_dir=output_dir,
        time_bucket="weekly",
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"✓ Weekly trend chart saved: {png_path_weekly}")
    
    # 4. Daily Granularity (for short-term decisions)
    print("\n" + "=" * 70)
    print("4. DAILY REVENUE TRACKING")
    print("=" * 70)
    print("\nBusiness Question: What are our daily revenue patterns?")
    print("Actionable Insights:")
    print("  • Immediate performance monitoring")
    print("  • Quick response to revenue dips")
    print("  • Daily operational adjustments")
    print()
    
    # Focus on recent month for daily analysis
    daily_start = "2025-11-01"
    daily_end = "2025-11-30"
    
    daily_df = aggregate_revenue_by_room_type(
        db_path=db_path,
        start_date=daily_start,
        end_date=daily_end,
        time_bucket="daily"
    )
    
    print(f"Daily Revenue for November 2025 (sample - first 10 days):")
    print(daily_df.head(10).to_string(index=False))
    print()
    
    # Summary Statistics
    print("\n" + "=" * 70)
    print("OVERALL BUSINESS PERFORMANCE SUMMARY")
    print("=" * 70)
    
    total_revenue = monthly_df['total_revenue'].sum()
    total_reservations = monthly_df['reservation_count'].sum()
    avg_booking_value = monthly_df['avg_cost_per_reservation'].mean()
    
    print(f"\n6-Month Performance (June - November 2025):")
    print(f"  Total Revenue: RM {total_revenue:,.2f}")
    print(f"  Total Completed Stays: {int(total_reservations)}")
    print(f"  Average Booking Value: RM {avg_booking_value:.2f}")
    print(f"  Monthly Average Revenue: RM {total_revenue/6:,.2f}")
    
    # ROI and decision-making recommendations
    print("\n" + "=" * 70)
    print("💡 STRATEGIC RECOMMENDATIONS")
    print("=" * 70)
    print()
    print("Based on the analytics, here's how to maximize profit:")
    print()
    print("1. DYNAMIC PRICING:")
    print("   • Increase rates during peak months (August/October)")
    print("   • Offer promotions during slower periods to maintain occupancy")
    print()
    print("2. ROOM MIX OPTIMIZATION:")
    
    top_performer = room_performance.index[0]
    print(f"   • Focus on {top_performer} rooms (highest revenue contributor)")
    print("   • Consider converting underperforming room types")
    print()
    print("3. MARKETING & SALES:")
    print("   • Target corporate clients for mid-week stays")
    print("   • Promote weekend packages for leisure travelers")
    print("   • Use data-driven forecasting for inventory management")
    print()
    print("4. OPERATIONAL EFFICIENCY:")
    print("   • Schedule more staff during high-revenue periods")
    print("   • Optimize maintenance during predictable slow periods")
    print("   • Monitor daily KPIs for quick decision-making")
    print()
    
    print("\n" + "=" * 70)
    print("✓ Analytics Reports Generated Successfully!")
    print("=" * 70)
    print(f"\nAll charts and data files saved to: {output_dir.absolute()}")
    print("\nUse these insights to:")
    print("  ✓ Make data-driven pricing decisions")
    print("  ✓ Optimize room allocation and staffing")
    print("  ✓ Identify growth opportunities")
    print("  ✓ Monitor performance trends")
    print("  ✓ Maximize revenue and profitability")
    print()

if __name__ == "__main__":
    main()
