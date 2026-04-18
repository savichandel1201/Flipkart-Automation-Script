import logging
import os
from datetime import datetime

def setup_logger(name=None):
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Use a specific logger name or a default
    logger = logging.getLogger(name if name else __name__)
    
    # Only add handlers if they haven't been added yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create a log filename with timestamp for each run
        # log_filename = f"logs/test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        # Or a constant filename for simplicity
        log_filename = "logs/automation.log"
        
        # File Handler
        file_handler = logging.FileHandler(log_filename, mode='a')
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger