from loguru import logger
from pathlib import Path

LOGS_DIR = Path(__file__).parent


def logging_configuration():
    logs_file = LOGS_DIR / "logs_history" / "foodram_logs.log"
    logger.remove()
    logger.add(
        logs_file,
        format="{time} {level} {message}",
        level="INFO",
        rotation="2 MB",
        compression="zip",
    )
