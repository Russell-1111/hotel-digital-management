from pathlib import Path
from app.rooms import load_config, AppConfig
import configparser


def test_load_config_defaults(tmp_path: Path):
    """Test loading config with defaults when file doesn't exist."""
    config_path = tmp_path / "config.ini"
    
    cfg = load_config(config_path)
    
    assert cfg.data_dir == Path('data')
    assert cfg.backup_dir == Path('backups')
    assert cfg.check_in_time == "14:00"
    assert cfg.check_out_time == "11:00"
    assert cfg.backup_time == "02:30"
    assert cfg.backup_retention_days == 7
    assert cfg.service_charge_rate == 0.10
    assert cfg.tax_rate == 0.06
    assert cfg.currency == "MYR"


def test_load_config_custom(tmp_path: Path):
    """Test loading config with custom values."""
    config_path = tmp_path / "config.ini"
    
    config_content = """[paths]
data_dir = custom_data
backup_dir = custom_backups

[ops]
check_in_time = 15:00
check_out_time = 12:00
backup_time = 03:00
backup_retention_days = 14

[finance]
service_charge_rate = 0.15
tax_rate = 0.08
currency = USD
"""
    config_path.write_text(config_content, encoding='utf-8')
    
    cfg = load_config(config_path)
    
    assert cfg.data_dir == Path('custom_data')
    assert cfg.backup_dir == Path('custom_backups')
    assert cfg.check_in_time == "15:00"
    assert cfg.check_out_time == "12:00"
    assert cfg.backup_time == "03:00"
    assert cfg.backup_retention_days == 14
    assert cfg.service_charge_rate == 0.15
    assert cfg.tax_rate == 0.08
    assert cfg.currency == "USD"


def test_config_partial_override(tmp_path: Path):
    """Test that partial config overrides defaults for specified values only."""
    config_path = tmp_path / "config.ini"
    
    config_content = """[finance]
tax_rate = 0.05
"""
    config_path.write_text(config_content, encoding='utf-8')
    
    cfg = load_config(config_path)
    
    # Custom value
    assert cfg.tax_rate == 0.05
    
    # Defaults preserved
    assert cfg.service_charge_rate == 0.10
    assert cfg.check_in_time == "14:00"
    assert cfg.currency == "MYR"
