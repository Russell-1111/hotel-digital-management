"""
Visualization module for Hotel Digital Management System.

Provides chart generation using matplotlib for revenue analytics by room type.
Supports trend line plots, bar charts, and combined views with PNG and CSV export.
"""

from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path
from typing import Literal, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

ChartType = Literal["trend", "bar", "combined"]


def generate_timestamp(timezone: str = "UTC") -> str:
    """
    Generate timestamp string for file naming.
    
    Args:
        timezone: Timezone name (e.g., "Asia/Kuala_Lumpur")
        
    Returns:
        Timestamp in format YYYYMMdd_HHmmss
        
    Example:
        >>> generate_timestamp("UTC")
        '20251112_143052'
    """
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    return now.strftime("%Y%m%d_%H%M%S")


def setup_chart_style():
    """
    Configure matplotlib style for consistent chart appearance.
    
    Sets:
        - Figure size: 12x8 inches (landscape)
        - DPI: 100 (good for screen and print)
        - Font sizes for readability
        - Grid enabled
    """
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['legend.fontsize'] = 9
    plt.rcParams['grid.alpha'] = 0.3


def generate_trend_chart(
    df: pd.DataFrame,
    title: str = "Revenue Trend by Room Type"
) -> plt.Figure:
    """
    Generate line plot showing average cost per reservation trends.
    
    Args:
        df: DataFrame with columns: time_bucket, room_type, avg_cost_per_reservation
        title: Chart title
        
    Returns:
        Matplotlib Figure object
        
    Notes:
        - One line per room type with distinct colors
        - X-axis: Time buckets (chronological)
        - Y-axis: Average cost per reservation (MYR)
        - Grid enabled for readability
        - Legend showing room types
    """
    setup_chart_style()
    fig, ax = plt.subplots()
    
    # Pivot data for plotting: rows=time_bucket, cols=room_type
    pivot = df.pivot(index='time_bucket', columns='room_type', values='avg_cost_per_reservation')
    
    # Plot each room type as a line
    for room_type in pivot.columns:
        ax.plot(pivot.index, pivot[room_type], marker='o', label=room_type, linewidth=2)
    
    ax.set_xlabel('Time Period')
    ax.set_ylabel('Average Cost per Reservation (MYR)')
    ax.set_title(title)
    ax.legend(title='Room Type', loc='best')
    ax.grid(True, alpha=0.3)
    
    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig


def generate_bar_chart(
    df: pd.DataFrame,
    title: str = "Total Revenue by Room Type"
) -> plt.Figure:
    """
    Generate grouped bar chart showing total revenue by room type.
    
    Args:
        df: DataFrame with columns: time_bucket, room_type, total_revenue, reservation_count
        title: Chart title
        
    Returns:
        Matplotlib Figure object
        
    Notes:
        - Grouped bars by room type (distinct colors)
        - X-axis: Time buckets
        - Y-axis (primary): Total revenue (MYR)
        - Optional secondary Y-axis: Reservation count overlay (line)
    """
    setup_chart_style()
    fig, ax1 = plt.subplots()
    
    # Pivot data for grouped bar chart
    pivot = df.pivot(index='time_bucket', columns='room_type', values='total_revenue')
    
    # Plot grouped bars
    pivot.plot(kind='bar', ax=ax1, width=0.8)
    
    ax1.set_xlabel('Time Period')
    ax1.set_ylabel('Total Revenue (MYR)', color='tab:blue')
    ax1.set_title(title)
    ax1.legend(title='Room Type', loc='upper left')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig


def generate_combined_chart(
    df: pd.DataFrame,
    title_prefix: str = "Revenue Analytics"
) -> plt.Figure:
    """
    Generate combined chart with trend line plot and bar chart as subplots.
    
    Args:
        df: DataFrame with columns: time_bucket, room_type, total_revenue, 
            avg_cost_per_reservation, reservation_count
        title_prefix: Prefix for subplot titles
        
    Returns:
        Matplotlib Figure object with 2 subplots
        
    Notes:
        - Top subplot: Trend line plot (avg cost per reservation)
        - Bottom subplot: Grouped bar chart (total revenue)
        - Shared X-axis for alignment
    """
    setup_chart_style()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Top: Trend line plot
    pivot_trend = df.pivot(index='time_bucket', columns='room_type', values='avg_cost_per_reservation')
    for room_type in pivot_trend.columns:
        ax1.plot(pivot_trend.index, pivot_trend[room_type], marker='o', label=room_type, linewidth=2)
    
    ax1.set_ylabel('Avg Cost per Reservation (MYR)')
    ax1.set_title(f'{title_prefix} - Trend (Avg Cost)')
    ax1.legend(title='Room Type', loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Bar chart
    pivot_revenue = df.pivot(index='time_bucket', columns='room_type', values='total_revenue')
    pivot_revenue.plot(kind='bar', ax=ax2, width=0.8)
    
    ax2.set_xlabel('Time Period')
    ax2.set_ylabel('Total Revenue (MYR)')
    ax2.set_title(f'{title_prefix} - Revenue')
    ax2.legend(title='Room Type', loc='upper left')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig


def save_chart_as_png(
    fig: plt.Figure,
    output_dir: Path,
    time_bucket: str,
    start_date: str,
    end_date: str,
    timezone: str = "UTC"
) -> Path:
    """
    Save matplotlib figure as PNG with timestamped filename.
    
    Args:
        fig: Matplotlib Figure object
        output_dir: Directory to save PNG file
        time_bucket: Time bucket type (for filename)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        timezone: Timezone for timestamp
        
    Returns:
        Path to saved PNG file
        
    Side Effects:
        - Creates output_dir if it doesn't exist
        - Saves PNG file with name: revenue_by_room_type_{bucket}_{start}_{end}_{timestamp}.png
        
    Raises:
        IOError: If unable to write to output directory
    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = generate_timestamp(timezone)
    filename = f"revenue_by_room_type_{time_bucket}_{start_date}_{end_date}_{timestamp}.png"
    filepath = output_dir / filename
    
    # Save figure
    fig.savefig(filepath, bbox_inches='tight', dpi=100)
    logger.info(f"Saved chart to {filepath}")
    
    # Close figure to free memory
    plt.close(fig)
    
    return filepath


def export_data_as_csv(
    df: pd.DataFrame,
    output_dir: Path,
    time_bucket: str,
    start_date: str,
    end_date: str,
    timezone: str = "UTC"
) -> Path:
    """
    Export DataFrame as CSV with timestamped filename.
    
    Args:
        df: DataFrame to export
        output_dir: Directory to save CSV file
        time_bucket: Time bucket type (for filename)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        timezone: Timezone for timestamp
        
    Returns:
        Path to saved CSV file
        
    Side Effects:
        - Creates output_dir if it doesn't exist
        - Saves CSV with headers and 2 decimal places for currency
        
    CSV Format:
        time_bucket,room_type,total_revenue,reservation_count,avg_cost_per_reservation
        2024-01,Deluxe,12500.00,10,1250.00
        ...
    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = generate_timestamp(timezone)
    filename = f"revenue_by_room_type_{time_bucket}_{start_date}_{end_date}_{timestamp}.csv"
    filepath = output_dir / filename
    
    # Export with proper formatting
    df.to_csv(filepath, index=False, float_format='%.2f')
    logger.info(f"Exported data to {filepath}")
    
    return filepath


def generate_and_export_analytics(
    df: pd.DataFrame,
    chart_type: ChartType,
    output_dir: Path,
    time_bucket: str,
    start_date: str,
    end_date: str,
    timezone: str = "UTC"
) -> Tuple[Path, Path]:
    """
    Generate chart and export both PNG and CSV files.
    
    Args:
        df: Aggregated revenue DataFrame
        chart_type: Type of chart to generate (trend/bar/combined)
        output_dir: Directory for output files
        time_bucket: Time bucket type
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        timezone: Timezone for timestamps
        
    Returns:
        Tuple of (png_path, csv_path)
        
    Raises:
        ValueError: If df is empty or chart_type is invalid
        IOError: If unable to write files
    """
    if df.empty:
        raise ValueError("Cannot generate chart from empty DataFrame")
    
    # Generate chart based on type
    title = f"Revenue Analytics ({start_date} to {end_date})"
    
    if chart_type == "trend":
        fig = generate_trend_chart(df, title=f"{title} - Trend")
    elif chart_type == "bar":
        fig = generate_bar_chart(df, title=f"{title} - Revenue")
    elif chart_type == "combined":
        fig = generate_combined_chart(df, title_prefix=title)
    else:
        raise ValueError(f"Invalid chart type: {chart_type}")
    
    # Save PNG
    png_path = save_chart_as_png(fig, output_dir, time_bucket, start_date, end_date, timezone)
    
    # Export CSV
    csv_path = export_data_as_csv(df, output_dir, time_bucket, start_date, end_date, timezone)
    
    return png_path, csv_path
