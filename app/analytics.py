"""
Revenue analytics module for Hotel Digital Management System.

Provides SQL-based aggregation of reservation revenue by room type with
configurable time bucketing (daily, weekly, monthly, quarterly).
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Dict, Literal
import pandas as pd

from .storage_sqlite import get_connection

logger = logging.getLogger(__name__)

TimeBucket = Literal["daily", "weekly", "monthly", "quarterly"]


def get_time_bucket_sql_expr(bucket: TimeBucket) -> str:
    """
    Get SQL expression for time bucket grouping.
    
    Args:
        bucket: Time bucket type (daily/weekly/monthly/quarterly)
        
    Returns:
        SQL expression string for GROUP BY clause
        
    Notes:
        - Daily: Extract date from start_date
        - Weekly: Compute week start (Sunday) using SQLite date functions
        - Monthly: Extract YYYY-MM from start_date
        - Quarterly: Compute YYYY-Q# from start_date
    """
    if bucket == "daily":
        # Simple date extraction: YYYY-MM-DD
        return "DATE(r.start_date)"
    elif bucket == "weekly":
        # Week start (Sunday): move to previous Sunday (weekday 0), then back 6 days
        return "DATE(r.start_date, 'weekday 0', '-6 days')"
    elif bucket == "monthly":
        # Extract YYYY-MM
        return "SUBSTR(r.start_date, 1, 7)"
    elif bucket == "quarterly":
        # Compute quarter: YYYY-Q# (quarter = (month - 1) / 3 + 1)
        return "SUBSTR(r.start_date, 1, 4) || '-Q' || ((CAST(SUBSTR(r.start_date, 6, 2) AS INTEGER) - 1) / 3 + 1)"
    else:
        raise ValueError(f"Invalid time bucket: {bucket}")


def aggregate_revenue_by_room_type(
    db_path: Path,
    start_date: str,
    end_date: str,
    time_bucket: TimeBucket = "monthly"
) -> pd.DataFrame:
    """
    Aggregate reservation revenue by room type over time.
    
    Args:
        db_path: Path to SQLite database
        start_date: Start date (YYYY-MM-DD format, inclusive)
        end_date: End date (YYYY-MM-DD format, inclusive)
        time_bucket: Time bucketing granularity (daily/weekly/monthly/quarterly)
        
    Returns:
        DataFrame with columns:
            - time_bucket: Time bucket label (format depends on bucket type)
            - room_type: Room type name
            - total_revenue: Sum of total_cost for the bucket
            - reservation_count: Number of reservations in the bucket
            - avg_cost_per_reservation: Average cost per reservation
            
    Notes:
        - Filters to reservations with status IN ('Checked-Out', 'Checked-In')
        - Only includes reservations where start_date is within [start_date, end_date]
        - Returns empty DataFrame if no data matches criteria
        
    Example:
        >>> df = aggregate_revenue_by_room_type(
        ...     db_path=Path("data/reservations.db"),
        ...     start_date="2024-01-01",
        ...     end_date="2024-12-31",
        ...     time_bucket="monthly"
        ... )
        >>> print(df.head())
           time_bucket room_type  total_revenue  reservation_count  avg_cost_per_reservation
        0      2024-01   Deluxe       12500.00                 10                   1250.00
        1      2024-01  Standard        8400.00                 15                    560.00
    """
    # Validate date format (basic check)
    if not (len(start_date) == 10 and len(end_date) == 10):
        raise ValueError("Dates must be in YYYY-MM-DD format")
    
    if not (start_date[4] == '-' and start_date[7] == '-' and 
            end_date[4] == '-' and end_date[7] == '-'):
        raise ValueError("Dates must be in YYYY-MM-DD format")
    
    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")
    
    # Build SQL query with time bucket expression
    time_expr = get_time_bucket_sql_expr(time_bucket)
    
    query = f"""
        SELECT
            {time_expr} AS time_bucket,
            rm.room_type,
            SUM(r.total_cost) AS total_revenue,
            COUNT(*) AS reservation_count,
            AVG(r.total_cost) AS avg_cost_per_reservation
        FROM reservations r
        JOIN rooms rm ON r.room_id = rm.room_id
        WHERE r.start_date >= ? AND r.start_date <= ?
          AND r.status IN ('Checked-Out', 'Checked-In')
        GROUP BY time_bucket, rm.room_type
        ORDER BY time_bucket, rm.room_type
    """
    
    try:
        with get_connection(db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            
            # Round numeric columns to 2 decimal places for currency
            if not df.empty:
                df['total_revenue'] = df['total_revenue'].round(2)
                df['avg_cost_per_reservation'] = df['avg_cost_per_reservation'].round(2)
            
            logger.info(
                f"Aggregated {len(df)} rows for {time_bucket} bucket "
                f"from {start_date} to {end_date}"
            )
            
            return df
            
    except Exception as e:
        logger.error(f"Error aggregating revenue data: {e}")
        raise


def format_bucket_label(bucket: TimeBucket) -> str:
    """
    Format time bucket type as display label.
    
    Args:
        bucket: Time bucket type
        
    Returns:
        Human-readable label
        
    Example:
        >>> format_bucket_label("monthly")
        'Monthly'
    """
    return bucket.capitalize()
