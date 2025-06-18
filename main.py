"""
MIFARE Classic Tool - ACR1252U Edition
Main application entry point
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from gui.main_window import MainWindow
from utils.logging_config import setup_logging

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting MIFARE Classic Tool - ACR1252U Edition")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("MIFARE Classic Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MIFARE Tools")
    
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    try:
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        # Start event loop
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Critical error during application startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
