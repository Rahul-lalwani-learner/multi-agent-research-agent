import logging
import sys
from typing import Optional

def setup_logger(name: str = "research_assistant", level: Optional[int] = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting
    
    Args:
        name: Logger name
        level: Logging level (defaults to INFO)
    
    Returns:
        Configured logger instance
    """
    if level is None:
        level = logging.INFO
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Default logger instance
logger = setup_logger()
