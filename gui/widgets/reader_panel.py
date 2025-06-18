"""
Reader status and control panel
"""

import logging
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from core.reader_manager import ReaderManager, ReaderStatus

logger = logging.getLogger(__name__)

class ReaderPanel(QGroupBox):
    """Reader status and control panel widget"""
    
    reader_connected = pyqtSignal()
    reader_disconnected = pyqtSignal()
    
    def __init__(self, reader_manager: ReaderManager):
        super().__init__("Reader Status")
        self.reader_manager = reader_manager
        self.setup_ui()
        self.update_ui()
        
        # Connect to reader status changes
        self.reader_manager.add_status_callback(self.on_reader_status_changed)
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Status display
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        # Reader selection
        reader_layout = QHBoxLayout()
        reader_layout.addWidget(QLabel("Reader:"))
        
        self.reader_combo = QComboBox()
        self.reader_combo.setMinimumWidth(200)
        reader_layout.addWidget(self.reader_combo)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_readers)
        reader_layout.addWidget(self.refresh_button)
        
        layout.addLayout(reader_layout)
        
        # Connection controls
        control_layout = QHBoxLayout()
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_reader)
        control_layout.addWidget(self.connect_button)
        
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_reader)
        self.disconnect_button.setEnabled(False)
        control_layout.addWidget(self.disconnect_button)
        
        layout.addLayout(control_layout)
        
        # Progress bar for connection
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Reader information
        info_layout = QVBoxLayout()
        
        self.name_label = QLabel("Name: -")
        info_layout.addWidget(self.name_label)
        
        self.firmware_label = QLabel("Firmware: -")
        info_layout.addWidget(self.firmware_label)
        
        layout.addLayout(info_layout)
        
        # Initial reader list refresh
        self.refresh_readers()
    
    def refresh_readers(self):
        """Refresh available readers list"""
        try:
            self.reader_combo.clear()
            readers = self.reader_manager.get_available_readers()
            
            if readers:
                self.reader_combo.addItems(readers)
                
                # Try to select ACR1252U if available
                acr_reader = self.reader_manager.find_acr1252u_reader()
                if acr_reader:
                    index = self.reader_combo.findText(acr_reader)
                    if index >= 0:
                        self.reader_combo.setCurrentIndex(index)
            else:
                self.reader_combo.addItem("No readers found")
                
        except Exception as e:
            logger.error(f"Error refreshing readers: {e}")
            self.reader_combo.clear()
            self.reader_combo.addItem("Error loading readers")
    
    def connect_reader(self):
        """Connect to selected reader"""
        try:
            selected_reader = self.reader_combo.currentText()
            
            if selected_reader and "No readers" not in selected_reader and "Error" not in selected_reader:
                self.show_progress("Connecting...")
                
                # Attempt connection
                success = self.reader_manager.connect(selected_reader)
                
                self.hide_progress()
                
                if success:
                    logger.info(f"Connected to reader: {selected_reader}")
                    self.reader_connected.emit()
                else:
                    logger.error(f"Failed to connect to reader: {selected_reader}")
            else:
                logger.warning("No valid reader selected")
                
        except Exception as e:
            logger.error(f"Error connecting to reader: {e}")
            self.hide_progress()
    
    def disconnect_reader(self):
        """Disconnect from reader"""
        try:
            self.reader_manager.disconnect()
            self.reader_disconnected.emit()
            logger.info("Disconnected from reader")
        except Exception as e:
            logger.error(f"Error disconnecting from reader: {e}")
    
    def on_reader_status_changed(self, status: str):
        """Handle reader status changes"""
        self.update_ui()
    
    def update_ui(self):
        """Update UI based on current reader status"""
        status = self.reader_manager.status
        info = self.reader_manager.get_reader_info()
        
        # Update status label and color
        status_colors = {
            ReaderStatus.DISCONNECTED: "color: red;",
            ReaderStatus.CONNECTING: "color: orange;",
            ReaderStatus.CONNECTED: "color: green;",
            ReaderStatus.ERROR: "color: red;"
        }
        
        self.status_label.setText(status.title())
        self.status_label.setStyleSheet(f"font-weight: bold; {status_colors.get(status, '')}")
        
        # Update buttons
        is_connected = status == ReaderStatus.CONNECTED
        is_connecting = status == ReaderStatus.CONNECTING
        
        self.connect_button.setEnabled(not is_connected and not is_connecting)
        self.disconnect_button.setEnabled(is_connected)
        self.reader_combo.setEnabled(not is_connected and not is_connecting)
        self.refresh_button.setEnabled(not is_connecting)
        
        # Update reader information
        self.name_label.setText(f"Name: {info['name'] or '-'}")
        self.firmware_label.setText(f"Firmware: {info['firmware_version'] or '-'}")
        
        # Hide progress if not connecting
        if status != ReaderStatus.CONNECTING:
            self.hide_progress()
    
    def show_progress(self, text: str):
        """Show progress bar with text"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setFormat(text)
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)
