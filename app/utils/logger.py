"""
Logging Configuration Module

This module sets up application-wide logging with:
- Colored console output for better readability
- File logging with daily rotation
- Separate error log file
- Configurable log levels
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class ColoredFormatter(logging.Formatter):
    """
    Custom log formatter with ANSI color codes for console output
    
    Makes logs easier to read by color-coding different log levels:
    - DEBUG: Grey
    - INFO: Blue
    - WARNING: Yellow
    - ERROR: Red
    - CRITICAL: Bold Red
    """
    
    # ANSI color codes
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    # Format string for each log level
    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    FORMATS = {
        logging.DEBUG: grey + format_string + reset,
        logging.INFO: blue + format_string + reset,
        logging.WARNING: yellow + format_string + reset,
        logging.ERROR: red + format_string + reset,
        logging.CRITICAL: bold_red + format_string + reset,
    }

    def format(self, record):
        """Format the log record with appropriate color"""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging(log_level: int = logging.INFO):
    """
    Setup application-wide logging configuration
    
    Creates three handlers:
    1. Console handler - Colored output to stdout
    2. File handler - All logs to daily log file
    3. Error handler - Only errors to separate file
    
    Args:
        log_level: Minimum log level to capture (default: INFO)
        
    Returns:
        Root logger instance
    """
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    root_logger.handlers = []
    
    # ===== CONSOLE HANDLER (with colors) =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredFormatter())
    root_logger.addHandler(console_handler)
    
    # ===== FILE HANDLER (all logs) =====
    log_file = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # ===== ERROR FILE HANDLER (errors only) =====
    error_file = LOG_DIR / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.FileHandler(error_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # ===== SUPPRESS NOISY THIRD-PARTY LOGGERS =====
    # HTTP libraries can be very verbose
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # LangChain can be verbose
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    # Log initial setup message
    root_logger.info("=" * 80)
    root_logger.info("🚀 Logging system initialized")
    root_logger.info(f"📁 Log directory: {LOG_DIR.absolute()}")
    root_logger.info(f"📝 Application log: {log_file.name}")
    root_logger.info(f"❌ Error log: {error_file.name}")
    root_logger.info(f"📊 Log level: {logging.getLevelName(log_level)}")
    root_logger.info("=" * 80)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Usage:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Hello world!")
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Logger instance configured with application settings
    """
    return logging.getLogger(name)


# Example usage and logging helper functions
def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Helper function to log function calls with parameters
    
    Args:
        logger: Logger instance
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    params = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.debug(f"🔧 Calling {func_name}({params})")


def log_execution_time(logger: logging.Logger, func_name: str, duration: float):
    """
    Helper function to log execution time
    
    Args:
        logger: Logger instance
        func_name: Name of the function
        duration: Execution time in seconds
    """
    logger.info(f"⏱️ {func_name} completed in {duration:.2f}s")