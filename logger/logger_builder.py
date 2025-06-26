import logging
from typing import Callable, List, Self

from .formatter import Formatter


class LoggerBuilder:
    """
    Builder class for constructing a custom logger with flexible configurations.
    """

    def __init__(self, name: str = "CustomLogger"):
        self._name = name
        self._level = logging.INFO
        self._formatter = Formatter()
        self._handlers: List[logging.Handler] = []

    def set_level(self, level: int) -> Self:
        """
        Sets the logging level of the logger.

        Args:
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO).

        Returns:
            LoggerBuilder: The builder instance for method chaining.
        """
        self._level = level
        return self

    def set_formatter(self, format_str: str) -> Self:
        """
        Sets a custom format for the log messages.

        Args:
            format_str (str): Format string for the logger.

        Returns:
            LoggerBuilder: The builder instance for method chaining.
        """
        self._formatter = Formatter(format_str)
        return self

    def add_stream_handler(self) -> Self:
        """
        Adds a stream handler to output logs to the console.

        Returns:
            LoggerBuilder: The builder instance for method chaining.
        """
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self._formatter)
        self._handlers.append(stream_handler)
        return self

    def add_file_handler(self, file_path: str, mode: str = "a") -> Self:
        """
        Adds a file handler to output logs to a specified file.

        Args:
            file_path (str): Path to the log file.
            mode (str): File mode (default is append mode 'a').

        Returns:
            LoggerBuilder: The builder instance for method chaining.
        """
        file_handler = logging.FileHandler(file_path, mode=mode)
        file_handler.setFormatter(self._formatter)
        self._handlers.append(file_handler)
        return self

    def build(self) -> logging.Logger:
        """
        Builds and returns the configured logger.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger = logging.getLogger(self._name)
        logger.setLevel(self._level)

        if not logger.handlers:
            for handler in self._handlers:
                logger.addHandler(handler)

        return logger

    def set_debug_mode(self, func: Callable):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(self._name)

            if self._level == logging.DEBUG:
                logger.debug(
                    f"Function {func.__name__} called with args: {args}, kwargs: {kwargs}"
                )

            result = func(*args, **kwargs)

            if self._level == logging.DEBUG:
                logger.debug(f"Function {func.__name__} returned: {result}")

            return result

        return wrapper