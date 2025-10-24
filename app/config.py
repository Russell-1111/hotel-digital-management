import configparser
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG = {
    'paths': {
        'data_dir': 'data',
        'backup_dir': 'backups'
    },
    'ops': {
        'check_in_time': '14:00',
        'check_out_time': '11:00',
        'backup_time': '02:30',
        'backup_retention_days': '7'
    },
    'finance': {
        'service_charge_rate': '0.10',
        'tax_rate': '0.06',
        'currency': 'MYR'
    }
}


@dataclass
class AppConfig:
    data_dir: Path
    backup_dir: Path
    check_in_time: str
    check_out_time: str
    backup_time: str
    backup_retention_days: int
    service_charge_rate: float
    tax_rate: float
    currency: str


def load_config(config_path: Path) -> AppConfig:
    cfg = configparser.ConfigParser()
    cfg.read_dict(DEFAULT_CONFIG)
    if config_path.exists():
        cfg.read(config_path)

    data_dir = Path(cfg['paths']['data_dir'])
    backup_dir = Path(cfg['paths']['backup_dir'])

    return AppConfig(
        data_dir=data_dir,
        backup_dir=backup_dir,
        check_in_time=cfg['ops']['check_in_time'],
        check_out_time=cfg['ops']['check_out_time'],
        backup_time=cfg['ops']['backup_time'],
        backup_retention_days=int(cfg['ops']['backup_retention_days']),
        service_charge_rate=float(cfg['finance']['service_charge_rate']),
        tax_rate=float(cfg['finance']['tax_rate']),
        currency=cfg['finance']['currency']
    )
