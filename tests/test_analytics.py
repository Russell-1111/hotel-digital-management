"""
Unit tests for analytics module.

Tests SQL aggregation logic for revenue analytics by room type
across different time buckets (daily, weekly, monthly, quarterly).
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime
import tempfile
import pandas as pd

from app.analytics import (
    aggregate_revenue_by_room_type,
    get_time_bucket_sql_expr,
    format_bucket_label
)
from app.storage_sqlite import get_connection, init_schema


@pytest.fixture
def temp_db():
    """Create a temporary database with test data."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    try:
        # Initialize schema
        with get_connection(db_path) as conn:
            init_schema(conn)
            
            # Insert test rooms
            conn.execute("""
                INSERT INTO rooms (room_id, room_type, base_price)
                VALUES 
                    ('101', 'Standard', 100.00),
                    ('201', 'Deluxe', 200.00),
                    ('301', 'Suite', 300.00)
            """)
            
            # Insert test reservations
            # Note: total_cost includes service charge + tax per billing rules
            test_reservations = [
                # Standard room reservations
                ('R001', '101', 'Alice', '123-456-7890', 'alice@example.com', 
                 '2024-01-05', '2024-01-07', 2, 'Checked-Out', 212.40, '2024-01-01 10:00:00', '2024-01-01 10:00:00'),
                ('R002', '101', 'Bob', '123-456-7891', 'bob@example.com', 
                 '2024-01-15', '2024-01-18', 2, 'Checked-Out', 318.60, '2024-01-10 10:00:00', '2024-01-10 10:00:00'),
                ('R003', '101', 'Charlie', '123-456-7892', 'charlie@example.com', 
                 '2024-02-10', '2024-02-12', 2, 'Checked-In', 212.40, '2024-02-01 10:00:00', '2024-02-01 10:00:00'),
                
                # Deluxe room reservations
                ('R004', '201', 'David', '123-456-7893', 'david@example.com', 
                 '2024-01-08', '2024-01-10', 2, 'Checked-Out', 424.80, '2024-01-02 10:00:00', '2024-01-02 10:00:00'),
                ('R005', '201', 'Eve', '123-456-7894', 'eve@example.com', 
                 '2024-02-05', '2024-02-08', 2, 'Checked-Out', 637.20, '2024-02-01 10:00:00', '2024-02-01 10:00:00'),
                
                # Cancelled reservation (should be excluded)
                ('R006', '301', 'Frank', '123-456-7895', 'frank@example.com', 
                 '2024-01-20', '2024-01-22', 2, 'Cancelled', 636.00, '2024-01-15 10:00:00', '2024-01-15 10:00:00'),
                
                # Suite reservation
                ('R007', '301', 'Grace', '123-456-7896', 'grace@example.com', 
                 '2024-03-10', '2024-03-12', 2, 'Checked-Out', 636.00, '2024-03-01 10:00:00', '2024-03-01 10:00:00'),
            ]
            
            for res in test_reservations:
                conn.execute("""
                    INSERT INTO reservations 
                    (id, room_id, guest_name, guest_phone, guest_email, 
                     start_date, end_date, num_guests, status, total_cost, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, res)
        
        yield db_path
        
    finally:
        # Cleanup
        db_path.unlink(missing_ok=True)


def test_get_time_bucket_sql_expr():
    """Test SQL expression generation for time buckets."""
    assert get_time_bucket_sql_expr("daily") == "DATE(r.start_date)"
    assert get_time_bucket_sql_expr("weekly") == "DATE(r.start_date, 'weekday 0', '-6 days')"
    assert get_time_bucket_sql_expr("monthly") == "SUBSTR(r.start_date, 1, 7)"
    assert "SUBSTR(r.start_date, 1, 4)" in get_time_bucket_sql_expr("quarterly")
    
    with pytest.raises(ValueError):
        get_time_bucket_sql_expr("invalid")


def test_format_bucket_label():
    """Test time bucket label formatting."""
    assert format_bucket_label("daily") == "Daily"
    assert format_bucket_label("weekly") == "Weekly"
    assert format_bucket_label("monthly") == "Monthly"
    assert format_bucket_label("quarterly") == "Quarterly"


def test_aggregate_monthly_bucket(temp_db):
    """Test monthly aggregation with multiple room types."""
    df = aggregate_revenue_by_room_type(
        temp_db,
        start_date="2024-01-01",
        end_date="2024-03-31",
        time_bucket="monthly"
    )
    
    # Should have data for Jan, Feb, Mar
    assert not df.empty
    assert len(df) > 0
    
    # Check columns
    expected_cols = ['time_bucket', 'room_type', 'total_revenue', 'reservation_count', 'avg_cost_per_reservation']
    assert list(df.columns) == expected_cols
    
    # Check January Standard room data
    jan_standard = df[(df['time_bucket'] == '2024-01') & (df['room_type'] == 'Standard')]
    assert len(jan_standard) == 1
    assert jan_standard.iloc[0]['reservation_count'] == 2  # R001, R002
    assert jan_standard.iloc[0]['total_revenue'] == pytest.approx(531.00, rel=0.01)  # 212.40 + 318.60
    
    # Check January Deluxe room data
    jan_deluxe = df[(df['time_bucket'] == '2024-01') & (df['room_type'] == 'Deluxe')]
    assert len(jan_deluxe) == 1
    assert jan_deluxe.iloc[0]['reservation_count'] == 1  # R004
    assert jan_deluxe.iloc[0]['total_revenue'] == pytest.approx(424.80, rel=0.01)
    
    # Check cancelled reservation is excluded
    jan_suite = df[(df['time_bucket'] == '2024-01') & (df['room_type'] == 'Suite')]
    assert len(jan_suite) == 0  # R006 is cancelled


def test_aggregate_daily_bucket(temp_db):
    """Test daily aggregation."""
    df = aggregate_revenue_by_room_type(
        temp_db,
        start_date="2024-01-01",
        end_date="2024-01-31",
        time_bucket="daily"
    )
    
    assert not df.empty
    
    # Check that dates are in YYYY-MM-DD format
    assert all(len(bucket) == 10 for bucket in df['time_bucket'])
    
    # Each reservation should appear on its start date
    jan_5 = df[df['time_bucket'] == '2024-01-05']
    assert len(jan_5) == 1
    assert jan_5.iloc[0]['room_type'] == 'Standard'


def test_aggregate_quarterly_bucket(temp_db):
    """Test quarterly aggregation."""
    df = aggregate_revenue_by_room_type(
        temp_db,
        start_date="2024-01-01",
        end_date="2024-12-31",
        time_bucket="quarterly"
    )
    
    assert not df.empty
    
    # Check Q1 data (Jan-Mar)
    q1_data = df[df['time_bucket'] == '2024-Q1']
    assert len(q1_data) > 0
    
    # Should have Standard, Deluxe, and Suite
    room_types = set(q1_data['room_type'])
    assert 'Standard' in room_types
    assert 'Deluxe' in room_types
    assert 'Suite' in room_types


def test_aggregate_empty_date_range(temp_db):
    """Test with date range that has no reservations."""
    df = aggregate_revenue_by_room_type(
        temp_db,
        start_date="2025-01-01",
        end_date="2025-12-31",
        time_bucket="monthly"
    )
    
    # Should return empty DataFrame
    assert df.empty
    assert len(df) == 0


def test_aggregate_single_room_type(temp_db):
    """Test aggregation when only one room type has reservations in range."""
    # Query only March (only Suite reservation)
    df = aggregate_revenue_by_room_type(
        temp_db,
        start_date="2024-03-01",
        end_date="2024-03-31",
        time_bucket="monthly"
    )
    
    assert not df.empty
    assert len(df) == 1
    assert df.iloc[0]['room_type'] == 'Suite'
    assert df.iloc[0]['reservation_count'] == 1


def test_aggregate_invalid_date_format(temp_db):
    """Test with invalid date format."""
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        aggregate_revenue_by_room_type(
            temp_db,
            start_date="01/01/2024",  # Wrong format
            end_date="2024-12-31",
            time_bucket="monthly"
        )


def test_aggregate_start_after_end(temp_db):
    """Test with start date after end date."""
    with pytest.raises(ValueError, match="before or equal"):
        aggregate_revenue_by_room_type(
            temp_db,
            start_date="2024-12-31",
            end_date="2024-01-01",
            time_bucket="monthly"
        )


def test_aggregate_filters_status(temp_db):
    """Test that only Checked-In and Checked-Out reservations are included."""
    df = aggregate_revenue_by_room_type(
        temp_db,
        start_date="2024-01-01",
        end_date="2024-12-31",
        time_bucket="monthly"
    )
    
    # Cancelled reservation R006 should not appear
    all_reservations = df['reservation_count'].sum()
    assert all_reservations == 6  # 7 total - 1 cancelled


def test_aggregate_numeric_precision(temp_db):
    """Test that numeric values are rounded to 2 decimal places."""
    df = aggregate_revenue_by_room_type(
        temp_db,
        start_date="2024-01-01",
        end_date="2024-12-31",
        time_bucket="monthly"
    )
    
    # Check that all revenue values have at most 2 decimal places
    for value in df['total_revenue']:
        assert round(value, 2) == value
    
    for value in df['avg_cost_per_reservation']:
        assert round(value, 2) == value
