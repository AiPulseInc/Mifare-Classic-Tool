"""
Logging configuration for the application
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from config.constants import AppSettings

def setup_logging(log_level=logging.INFO, enable_file_logging=True):
    """Setup application logging configuration"""
    
    # Create logs directory
    log_dir = Path.home() / ".mifare_classic_tool" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if enable_file_logging:
        log_file = log_dir / AppSettings.LOG_FILE_NAME
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=AppSettings.LOG_MAX_SIZE,
            backupCount=AppSettings.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # More verbose for file
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('smartcard').setLevel(logging.WARNING)  # Reduce smartcard noise
    
    logging.info("Logging initialized")
