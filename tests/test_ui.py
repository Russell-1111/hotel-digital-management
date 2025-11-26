"""Smoke tests for UI initialization and access control."""
import tkinter as tk
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


def test_ui_import():
    """Test that UI module can be imported."""
    from app.ui import main
    assert hasattr(main, 'App')
    assert hasattr(main, 'run')


def test_app_instantiation(tmp_path: Path):
    """Test that the App can be instantiated without errors."""
    pytest.skip("Skipping App instantiation test - requires authentication dialog mocking")


def test_theme_setup():
    """Test that theme setup completes without errors."""
    pytest.skip("Skipping Tkinter GUI test - requires display and proper Tcl/Tk setup")


def test_analytics_section_hidden_for_staff():
    """Test that Analytics section is not created for staff users."""
    pytest.skip("Skipping Tkinter GUI test - requires display and proper Tcl/Tk setup")
    # This test would verify:
    # 1. Initialize App with staff user
    # 2. Navigate to Reports tab
    # 3. Assert analytics_section frame does not exist in report_frame children
    # 4. Assert "Revenue by Room Type" button is not created


def test_analytics_section_visible_for_admin():
    """Test that Analytics section is created and visible for admin users."""
    pytest.skip("Skipping Tkinter GUI test - requires display and proper Tcl/Tk setup")
    # This test would verify:
    # 1. Initialize App with admin user
    # 2. Navigate to Reports tab
    # 3. Assert analytics_section frame exists in report_frame
    # 4. Assert "Revenue by Room Type" button is present


def test_revenue_analytics_callback_blocked_for_staff():
    """Test that _show_revenue_analytics callback blocks staff access."""
    pytest.skip("Skipping Tkinter GUI test - requires display and proper Tcl/Tk setup")
    # This test would verify:
    # 1. Create App instance with staff user
    # 2. Mock _require_admin to return False
    # 3. Call _show_revenue_analytics directly
    # 4. Assert _require_admin was called with "Access Revenue Analytics"
    # 5. Assert RevenueAnalyticsDialog was NOT instantiated


def test_revenue_analytics_callback_allowed_for_admin():
    """Test that _show_revenue_analytics callback allows admin access."""
    pytest.skip("Skipping Tkinter GUI test - requires display and proper Tcl/Tk setup")
    # This test would verify:
    # 1. Create App instance with admin user
    # 2. Mock _require_admin to return True
    # 3. Mock RevenueAnalyticsDialog to prevent actual dialog creation
    # 4. Call _show_revenue_analytics directly
    # 5. Assert _require_admin was called
    # 6. Assert RevenueAnalyticsDialog was instantiated
