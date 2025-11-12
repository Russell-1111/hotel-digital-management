"""
Functional tests for visualization module.

Tests chart generation (trend, bar, combined) and file export (PNG, CSV)
using sample data.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil

from app.visualization import (
    generate_trend_chart,
    generate_bar_chart,
    generate_combined_chart,
    save_chart_as_png,
    export_data_as_csv,
    generate_and_export_analytics,
    generate_timestamp
)


@pytest.fixture
def sample_data():
    """Create sample revenue data for testing."""
    data = {
        'time_bucket': ['2024-01', '2024-01', '2024-02', '2024-02', '2024-03', '2024-03'],
        'room_type': ['Standard', 'Deluxe', 'Standard', 'Deluxe', 'Standard', 'Deluxe'],
        'total_revenue': [500.00, 1200.00, 600.00, 1400.00, 550.00, 1300.00],
        'reservation_count': [5, 6, 6, 7, 5, 6],
        'avg_cost_per_reservation': [100.00, 200.00, 100.00, 200.00, 110.00, 216.67]
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for output files."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_generate_timestamp():
    """Test timestamp generation."""
    ts = generate_timestamp("UTC")
    
    # Should be in format YYYYMMdd_HHmmss
    assert len(ts) == 15
    assert ts[8] == '_'
    
    # Should be parseable as datetime components
    date_part = ts[:8]
    time_part = ts[9:]
    assert date_part.isdigit()
    assert time_part.isdigit()


def test_generate_trend_chart(sample_data):
    """Test trend line plot generation."""
    fig = generate_trend_chart(sample_data, title="Test Trend")
    
    # Check figure was created
    assert fig is not None
    
    # Check axes
    axes = fig.get_axes()
    assert len(axes) == 1
    
    ax = axes[0]
    assert ax.get_xlabel() == 'Time Period'
    assert 'Average Cost' in ax.get_ylabel()
    assert 'Test Trend' in ax.get_title()
    
    # Check legend exists
    legend = ax.get_legend()
    assert legend is not None
    
    # Should have 2 lines (Standard and Deluxe)
    lines = ax.get_lines()
    assert len(lines) == 2


def test_generate_bar_chart(sample_data):
    """Test grouped bar chart generation."""
    fig = generate_bar_chart(sample_data, title="Test Bar Chart")
    
    # Check figure was created
    assert fig is not None
    
    # Check axes
    axes = fig.get_axes()
    assert len(axes) == 1
    
    ax = axes[0]
    assert ax.get_xlabel() == 'Time Period'
    assert 'Total Revenue' in ax.get_ylabel()
    assert 'Test Bar Chart' in ax.get_title()


def test_generate_combined_chart(sample_data):
    """Test combined chart with subplots."""
    fig = generate_combined_chart(sample_data, title_prefix="Test Combined")
    
    # Check figure was created
    assert fig is not None
    
    # Should have 2 subplots
    axes = fig.get_axes()
    assert len(axes) == 2
    
    # Check top subplot (trend)
    ax_trend = axes[0]
    assert 'Avg Cost' in ax_trend.get_ylabel()
    assert 'Trend' in ax_trend.get_title()
    
    # Check bottom subplot (bar)
    ax_bar = axes[1]
    assert 'Revenue' in ax_bar.get_ylabel()
    assert 'Time Period' in ax_bar.get_xlabel()


def test_save_chart_as_png(sample_data, temp_output_dir):
    """Test saving chart as PNG file."""
    fig = generate_trend_chart(sample_data)
    
    png_path = save_chart_as_png(
        fig,
        temp_output_dir,
        time_bucket="monthly",
        start_date="2024-01-01",
        end_date="2024-03-31",
        timezone="UTC"
    )
    
    # Check file exists
    assert png_path.exists()
    assert png_path.suffix == '.png'
    
    # Check filename format
    assert 'revenue_by_room_type' in png_path.name
    assert 'monthly' in png_path.name
    assert '2024-01-01' in png_path.name
    assert '2024-03-31' in png_path.name
    
    # Check file is not empty
    assert png_path.stat().st_size > 0


def test_export_data_as_csv(sample_data, temp_output_dir):
    """Test CSV export with proper formatting."""
    csv_path = export_data_as_csv(
        sample_data,
        temp_output_dir,
        time_bucket="monthly",
        start_date="2024-01-01",
        end_date="2024-03-31",
        timezone="UTC"
    )
    
    # Check file exists
    assert csv_path.exists()
    assert csv_path.suffix == '.csv'
    
    # Read back and validate
    df_read = pd.read_csv(csv_path)
    
    # Check headers
    expected_cols = ['time_bucket', 'room_type', 'total_revenue', 'reservation_count', 'avg_cost_per_reservation']
    assert list(df_read.columns) == expected_cols
    
    # Check row count
    assert len(df_read) == len(sample_data)
    
    # Check data matches
    assert df_read['room_type'].tolist() == sample_data['room_type'].tolist()
    
    # Check numeric formatting (should be 2 decimal places)
    for value in df_read['total_revenue']:
        # CSV may read as float, check it matches original with 2 decimal precision
        assert isinstance(value, (int, float))


def test_generate_and_export_analytics_trend(sample_data, temp_output_dir):
    """Test full workflow: generate trend chart and export both PNG and CSV."""
    png_path, csv_path = generate_and_export_analytics(
        sample_data,
        chart_type="trend",
        output_dir=temp_output_dir,
        time_bucket="monthly",
        start_date="2024-01-01",
        end_date="2024-03-31",
        timezone="UTC"
    )
    
    # Check both files exist
    assert png_path.exists()
    assert csv_path.exists()
    
    # Check files are not empty
    assert png_path.stat().st_size > 0
    assert csv_path.stat().st_size > 0
    
    # Check filenames have same timestamp
    png_timestamp = png_path.stem.split('_')[-1]
    csv_timestamp = csv_path.stem.split('_')[-1]
    assert png_timestamp == csv_timestamp


def test_generate_and_export_analytics_bar(sample_data, temp_output_dir):
    """Test bar chart generation and export."""
    png_path, csv_path = generate_and_export_analytics(
        sample_data,
        chart_type="bar",
        output_dir=temp_output_dir,
        time_bucket="monthly",
        start_date="2024-01-01",
        end_date="2024-03-31",
        timezone="UTC"
    )
    
    assert png_path.exists()
    assert csv_path.exists()


def test_generate_and_export_analytics_combined(sample_data, temp_output_dir):
    """Test combined chart generation and export."""
    png_path, csv_path = generate_and_export_analytics(
        sample_data,
        chart_type="combined",
        output_dir=temp_output_dir,
        time_bucket="monthly",
        start_date="2024-01-01",
        end_date="2024-03-31",
        timezone="UTC"
    )
    
    assert png_path.exists()
    assert csv_path.exists()


def test_generate_and_export_creates_output_dir(sample_data):
    """Test that output directory is created if it doesn't exist."""
    # Use a directory that doesn't exist yet
    non_existent_dir = Path(tempfile.gettempdir()) / "test_analytics_output_12345"
    
    # Ensure it doesn't exist
    if non_existent_dir.exists():
        shutil.rmtree(non_existent_dir)
    
    try:
        png_path, csv_path = generate_and_export_analytics(
            sample_data,
            chart_type="trend",
            output_dir=non_existent_dir,
            time_bucket="monthly",
            start_date="2024-01-01",
            end_date="2024-03-31",
            timezone="UTC"
        )
        
        # Check directory was created
        assert non_existent_dir.exists()
        assert png_path.exists()
        assert csv_path.exists()
        
    finally:
        # Cleanup
        if non_existent_dir.exists():
            shutil.rmtree(non_existent_dir)


def test_generate_and_export_empty_dataframe(temp_output_dir):
    """Test error handling with empty DataFrame."""
    empty_df = pd.DataFrame(columns=['time_bucket', 'room_type', 'total_revenue', 'reservation_count', 'avg_cost_per_reservation'])
    
    with pytest.raises(ValueError, match="empty DataFrame"):
        generate_and_export_analytics(
            empty_df,
            chart_type="trend",
            output_dir=temp_output_dir,
            time_bucket="monthly",
            start_date="2024-01-01",
            end_date="2024-03-31",
            timezone="UTC"
        )


def test_generate_and_export_invalid_chart_type(sample_data, temp_output_dir):
    """Test error handling with invalid chart type."""
    with pytest.raises(ValueError, match="Invalid chart type"):
        generate_and_export_analytics(
            sample_data,
            chart_type="invalid",
            output_dir=temp_output_dir,
            time_bucket="monthly",
            start_date="2024-01-01",
            end_date="2024-03-31",
            timezone="UTC"
        )


def test_csv_matches_chart_data(sample_data, temp_output_dir):
    """Test that exported CSV contains exactly the data visualized in chart."""
    png_path, csv_path = generate_and_export_analytics(
        sample_data,
        chart_type="combined",
        output_dir=temp_output_dir,
        time_bucket="monthly",
        start_date="2024-01-01",
        end_date="2024-03-31",
        timezone="UTC"
    )
    
    # Read CSV
    df_csv = pd.read_csv(csv_path)
    
    # Check row count matches
    assert len(df_csv) == len(sample_data)
    
    # Check data values match (allowing for floating point precision)
    for i in range(len(sample_data)):
        assert df_csv.loc[i, 'time_bucket'] == sample_data.loc[i, 'time_bucket']
        assert df_csv.loc[i, 'room_type'] == sample_data.loc[i, 'room_type']
        assert abs(df_csv.loc[i, 'total_revenue'] - sample_data.loc[i, 'total_revenue']) < 0.01
