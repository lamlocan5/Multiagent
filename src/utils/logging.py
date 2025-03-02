import logging
import os
import sys
from typing import Optional
from datetime import datetime

# Configure basic logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure formatter
formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Name of the logger, typically the module name
        log_level: Optional override for the default log level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level
    level = getattr(logging, log_level or LOG_LEVEL)
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler for this logger
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"{today}_{name.replace('.', '_')}.log")
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def setup_global_logging(log_level: Optional[str] = None):
    """
    Configure global logging settings.
    
    Args:
        log_level: Optional log level to set
    """
    level = getattr(logging, log_level or LOG_LEVEL)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Add console handler to root logger
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler to root logger
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"{today}_app.log")
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
