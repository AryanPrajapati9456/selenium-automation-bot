import logging
import os
from datetime import datetime

def setup_logging(log_level=logging.INFO):
    """
    Set up logging configuration for the automation framework.
    
    Args:
        log_level: Logging level (default: INFO)
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Generate timestamp for log file names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Configure base logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            # File handler for general logs
            logging.FileHandler(f"logs/app_{timestamp}.log"),
            
            # File handler for errors
            logging.FileHandler(f"logs/error_{timestamp}.log"),
            
            # Console handler
            logging.StreamHandler()
        ]
    )
    
    # Set error handler to only log errors and above
    error_handler = logging.FileHandler(f"logs/error_{timestamp}.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    
    # Add error handler to root logger
    logging.getLogger().addHandler(error_handler)
    
    logging.info("Logging setup completed")


def get_logger(name):
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)