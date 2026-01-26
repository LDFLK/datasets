import logging
import sys

# Define custom success level
SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)

# Monkey patch logger
logging.Logger.success = success

class ColoredFormatter(logging.Formatter):
    """Custom logging formatter with colors."""
    
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"  # Blue for INFO
    green = "\x1b[32;20m" # Green for SUCCESS
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    # Format: [TIMESTAMP] [LEVEL] Message
    format_str = "[%(asctime)s] [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: blue + format_str + reset,
        SUCCESS_LEVEL: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger(name: str = "ingestion", level=logging.INFO):
    """Set up and return a logger with colored output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent adding multiple handlers if function is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColoredFormatter())
        logger.addHandler(handler)
        
    return logger

# Global logger instance
logger = setup_logger()

