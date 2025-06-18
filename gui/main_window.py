"""
Main application window
"""

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QStatusBar, QMenuBar, QAction, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from config.constants import AppSettings
from config.settings import settings
from core.reader_manager import ReaderManager, ReaderStatus
from core.card_operations import CardOperations
from core.authentication import AuthenticationManager
from gui.widgets.reader_panel import ReaderPanel
from gui.widgets.card_panel import CardPanel
from gui.widgets.auth_panel import AuthPanel
from gui.widgets.block_panel import BlockPanel
from gui.widgets.security_panel import SecurityPanel

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.reader_manager = ReaderManager()
        self.card_operations = CardOperations(self.reader_manager)
        self.auth_manager = AuthenticationManager(self.reader_manager, self.card_operations)
        
        # Setup UI
        self.setup_ui()
        self.setup_menus()
        self.setup_status_bar()
        self.setup_connections()
        
        # Setup timers
        self.card_monitor_timer = QTimer()
        self.card_monitor_timer.timeout.connect(self.monitor_card)
        self.card_monitor_timer.start(1000)  # Check every second
        
        # Auto-connect if enabled
        if settings.get('reader.auto_connect', True):
            QTimer.singleShot(500, self.auto_connect_reader)
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(AppSettings.WINDOW_TITLE)
        self.setMinimumSize(AppSettings.WINDOW_MIN_WIDTH, AppSettings.WINDOW_MIN_HEIGHT)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Reader and Card info
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Reader panel
        self.reader_panel = ReaderPanel(self.reader_manager)
        left_layout.addWidget(self.reader_panel)
        
        # Card panel
        self.card_panel = CardPanel(self.card_operations)
        left_layout.addWidget(self.card_panel)
        
        # Authentication panel
        self.auth_panel = AuthPanel(self.auth_manager, self.card_operations)
        left_layout.addWidget(self.auth_panel)
        
        left_layout.addStretch()
        splitter.addWidget(left_panel)
        
        # Right panel - Operations
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Block operations panel
        self.block_panel = BlockPanel(self.card_operations, self.auth_manager)
        right_layout.addWidget(self.block_panel)
        
        # Security operations panel
        self.security_panel = SecurityPanel(self.card_operations, self.auth_manager)
        right_layout.addWidget(self.security_panel)
        
        right_layout.addStretch()
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 500])
    
    def setup_menus(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        connect_action = QAction('&Connect Reader', self)
        connect_action.triggered.connect(self.reader_panel.connect_reader)
        file_menu.addAction(connect_action)
        
        disconnect_action = QAction('&Disconnect Reader', self)
        disconnect_action.triggered.connect(self.reader_panel.disconnect_reader)
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        refresh_action = QAction('&Refresh Card', self)
        refresh_action.triggered.connect(self.refresh_card)
        tools_menu.addAction(refresh_action)
        
        clear_auth_action = QAction('&Clear Authentication', self)
        clear_auth_action.triggered.connect(self.clear_authentication)
        tools_menu.addAction(clear_auth_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def setup_connections(self):
        """Setup signal connections between components"""
        # Reader status changes
        self.reader_manager.add_status_callback(self.on_reader_status_changed)
        
        # Authentication success updates
        self.auth_panel.authentication_success.connect(self.on_authentication_success)
        
        # Block operations updates
        self.block_panel.operation_completed.connect(self.on_operation_completed)
    
    def auto_connect_reader(self):
        """Auto-connect to reader if available"""
        try:
            self.reader_panel.connect_reader()
        except Exception as e:
            logger.warning(f"Auto-connect failed: {e}")
    
    def monitor_card(self):
        """Monitor card presence"""
        if self.reader_manager.is_connected():
            try:
                card_present = self.card_operations.detect_card()
                self.card_panel.update_card_info()
            except Exception as e:
                logger.debug(f"Card monitoring error: {e}")
    
    def on_reader_status_changed(self, status: str):
        """Handle reader status changes"""
        status_messages = {
            ReaderStatus.DISCONNECTED: "Reader disconnected",
            ReaderStatus.CONNECTING: "Connecting to reader...",
            ReaderStatus.CONNECTED: "Reader connected",
            ReaderStatus.ERROR: "Reader error"
        }
        
        message = status_messages.get(status, f"Reader status: {status}")
        self.status_bar.showMessage(message)
        
        # Update UI components
        self.card_panel.update_card_info()
        self.auth_panel.update_ui_state()
        self.block_panel.update_ui_state()
    
    def on_authentication_success(self, sector: int):
        """Handle successful authentication"""
        self.status_bar.showMessage(f"Sector {sector} authenticated successfully")
        self.block_panel.update_ui_state()
    
    def on_operation_completed(self, operation: str, success: bool):
        """Handle completed operations"""
        if success:
            self.status_bar.showMessage(f"{operation} completed successfully")
        else:
            self.status_bar.showMessage(f"{operation} failed")
    
    def refresh_card(self):
        """Refresh card information"""
        if self.reader_manager.is_connected():
            self.card_operations.detect_card()
            self.card_panel.update_card_info()
            self.status_bar.showMessage("Card information refreshed")
    
    def clear_authentication(self):
        """Clear all authentication states"""
        self.auth_manager.clear_loaded_keys()
        self.status_bar.showMessage("Authentication cleared")
        self.auth_panel.update_ui_state()
        self.block_panel.update_ui_state()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About MIFARE Classic Tool",
            f"""
            <h3>MIFARE Classic Tool - ACR1252U Edition</h3>
            <p>Version 1.0.0</p>
            <p>A comprehensive tool for MIFARE Classic card operations using ACR1252U reader.</p>
            <p><b>Features:</b></p>
            <ul>
            <li>Card detection and information</li>
            <li>Authentication with Key A/B</li>
            <li>Block read/write operations</li>
            <li>Security operations</li>
            </ul>
            <p><b>Hardware:</b> ACR1252U NFC Reader required</p>
            """
        )
    
    def closeEvent(self, event):
        """Handle application close"""
        try:
            # Stop timers
            self.card_monitor_timer.stop()
            
            # Disconnect reader
            if self.reader_manager.is_connected():
                self.reader_manager.disconnect()
            
            # Save settings
            settings.save_settings()
            
            event.accept()
        except Exception as e:
            logger.error(f"Error during application close: {e}")
            event.accept()
