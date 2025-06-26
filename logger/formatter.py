import logging

from .colors import ColorCodes


class Formatter(logging.Formatter):
    """
    Custom logging formatter with colors for different log levels,
    a specific date format, and customized spacing.
    """

    COLOR_CODES: ColorCodes = {
        "time": "\033[37m",  # White for timestamp
        "name": "\033[94m",  # Blue for logger name
        "level": {
            logging.DEBUG: "\033[92m",  # Green for DEBUG level
            logging.INFO: "\033[96m",  # Cyan for INFO level
            logging.WARNING: "\033[93m",  # Yellow for WARNING level
            logging.ERROR: "\033[91m",  # Red for ERROR level
            logging.CRITICAL: "\033[95m",  # Magenta for CRITICAL level
        },
        "message": "\033[33m",  # Yellow for the message
        "reset": "\033[0m",  # Reset color
    }

    def __init__(self, log_format: str = "", date_format: str = ""):
        if not log_format:
            log_format = "[%(asctime)s]  - (%(name)-s) - [%(levelname)-s] - %(message)s"

        if not date_format:
            date_format = "%d/%m/%Y %H:%M:%S"

        super().__init__(fmt=log_format, datefmt=date_format)

    def format(self, record: logging.LogRecord) -> str:
        time_color = self.COLOR_CODES["name"]
        name_color = self.COLOR_CODES["name"]
        level_color = self.COLOR_CODES["level"].get(record.levelno, "")
        message_color = self.COLOR_CODES["message"]
        reset_color = self.COLOR_CODES["reset"]

        record.asctime = (
            f"{time_color}{self.formatTime(record, self.datefmt)}{reset_color}"
        )
        record.name = f"{name_color}{record.name}{reset_color}"
        record.levelname = f"{level_color}{record.levelname}{reset_color}"
        record.msg = f"{message_color}{record.msg}{reset_color}"
        return super().format(record)