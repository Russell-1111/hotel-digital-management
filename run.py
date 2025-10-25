from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler
from app.ui.main import run


def setup_logging() -> None:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "app.log"

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Reset handlers to avoid duplicates on reload
    root.handlers.clear()

    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(console_handler)


if __name__ == "__main__":
    setup_logging()
    logging.getLogger(__name__).info("Starting Hotel Digital Management UI")
    run()
