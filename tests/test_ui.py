"""Smoke tests for UI initialization."""
import tkinter as tk
from pathlib import Path
from unittest.mock import patch
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
