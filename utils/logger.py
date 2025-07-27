"""
Logging utility for the AI Personal Assistant
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from config import LOG_LEVEL, LOG_FILE

def setup_logger(name: str = "assistant") -> logging.Logger:
    """
    Set up and configure logger for the assistant.
    
    Args:
        name (str): Name of the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_user_interaction(user_input: str, response: str, logger: logging.Logger):
    """
    Log user interactions for analysis and debugging.
    
    Args:
        user_input (str): What the user said
        response (str): Assistant's response
        logger (logging.Logger): Logger instance
    """
    logger.info(f"USER: {user_input}")
    logger.info(f"ASSISTANT: {response}")
    
def log_error(error: Exception, context: str, logger: logging.Logger):
    """
    Log errors with context for debugging.
    
    Args:
        error (Exception): The exception that occurred
        context (str): Context where the error occurred
        logger (logging.Logger): Logger instance
    """
    logger.error(f"ERROR in {context}: {str(error)}", exc_info=True)