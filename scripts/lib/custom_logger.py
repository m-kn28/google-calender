import logging
import logging.handlers

from config.config import LOGGING_BACKUP_COUNT, LOGGING_INTERVAL, LOGGING_FILE_PATH


def setup_logger(file_path: str = "./application.log", interval: int = 1, backup_count: int = 30) -> logging.Logger:
    # Set the logger and handler
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = logging.handlers.TimedRotatingFileHandler(
        file_path, when='midnight', interval=interval, backupCount=backup_count, encoding='utf-8', delay=False, utc=False
    )
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s, %(levelname)s, [%(funcName)s], %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logger(file_path=LOGGING_FILE_PATH,
                      interval=LOGGING_INTERVAL, backup_count=LOGGING_BACKUP_COUNT)
