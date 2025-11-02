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
    from app.ui.main import App
    
    # Create minimal config
    config_content = """[paths]
data_dir = data
backup_dir = backups

[ops]
check_in_time = 14:00
check_out_time = 11:00
backup_time = 02:30
backup_retention_days = 7

[finance]
service_charge_rate = 0.10
tax_rate = 0.06
currency = MYR
"""
    config_path = tmp_path / "config.ini"
    config_path.write_text(config_content, encoding='utf-8')
    
    # Create data directories and files
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "rooms.csv").write_text("room_id,room_type,base_price\n101,Standard,100.00\n", encoding='utf-8')
    (data_dir / "reservations.csv").write_text("reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at\n", encoding='utf-8')
    
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    
    # Mock backup scheduler to avoid background threads in tests
    with patch('app.ui.main.start_daily_backup_scheduler'):
        with patch('app.ui.main.load_config') as mock_config:
            from app.rooms import load_config as real_load_config
            cfg = real_load_config(config_path)
            # Override paths to use tmp_path
            cfg.data_dir = data_dir
            cfg.backup_dir = backup_dir
            mock_config.return_value = cfg
            
            # Instantiate without showing window
            app = App()
            
            # Verify basic attributes
            assert app.title() == "Hotel Digital Management - Front Desk"
            assert hasattr(app, 'ops_frame')
            assert hasattr(app, 'res_frame')
            assert hasattr(app, 'avail_frame')
            assert hasattr(app, 'report_frame')
            
            # Clean up
            app.destroy()


def test_theme_setup():
    """Test that theme setup completes without errors."""
    pytest.skip("Skipping Tkinter GUI test - requires display and proper Tcl/Tk setup")
