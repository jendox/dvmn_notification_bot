import logging
import queue

from devman import DEVMAN_LOGGER_NAME
from tg_bot import BOT_LOGGER_NAME

LOGGER_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class LogsHandler(logging.Handler):
    def __init__(self, logs_queue: queue.Queue[logging.LogRecord]):
        super().__init__()
        self.queue = logs_queue

    def emit(self, record: logging.LogRecord) -> None:
        self.queue.put(record)


def setup_logging(logs_queue: queue.Queue[logging.LogRecord]) -> None:
    log_handler = LogsHandler(logs_queue)
    log_handler.setLevel(logging.INFO)
    log_handler.setFormatter(logging.Formatter(LOGGER_FORMAT))
    logging.getLogger(BOT_LOGGER_NAME).addHandler(log_handler)
    logging.getLogger(DEVMAN_LOGGER_NAME).addHandler(log_handler)
