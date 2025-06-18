"""
Card information display panel
"""

import logging
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from core.card_operations import CardOperations
from core.data_utils import bytes_to_hex_string

logger = logging.getLogger(__name__)

class CardPanel(QGroupBox):
    """Card information display panel"""
    
    card_detected = pyqtSignal()
    card_removed = pyqtSignal()
    
    def __init__(self, card_operations: CardOperations):
        super().__init__("Card Information")
        self.card_operations = card_operations
        self.setup_ui()
        self.update_card_info()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Card status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        
        self.status_label = QLabel("No card")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        # Card information
        info_layout = QVBoxLayout()
        
        self.type_label = QLabel("Type: -")
        info_layout.addWidget(self.type_label)
        
        self.uid_label = QLabel("UID: -")
        self.uid_label.setFont(QFont("Courier", 9))
        info_layout.addWidget(self.uid_label)
        
        self.size_label = QLabel("Size: -")
        info_layout.addWidget(self.size_label)
        
        self.sectors_label = QLabel("Sectors: -")
        info_layout.addWidget(self.sectors_label)
        
        layout.addLayout(info_layout)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_card)
        layout.addWidget(self.refresh_button)
    
    def update_card_info(self):
        """Update card information display"""
        card_info = self.card_operations.get_card_info()
        
        if card_info.present:
            # Card present
            self.status_label.setText("Present")
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
            
            self.type_label.setText(f"Type: {card_info.get_card_type_name()}")
            
            if card_info.uid:
                uid_hex = bytes_to_hex_string(card_info.uid)
                self.uid_label.setText(f"UID: {uid_hex}")
            else:
                self.uid_label.setText("UID: -")
            
            if card_info.size > 0:
                self.size_label.setText(f"Size: {card_info.size} bytes")
            else:
                self.size_label.setText("Size: -")
            
            sectors = card_info.get_sector_count()
            if sectors > 0:
                self.sectors_label.setText(f"Sectors: {sectors}")
            else:
                self.sectors_label.setText("Sectors: -")
            
            self.card_detected.emit()
        else:
            # No card
            self.status_label.setText("No card")
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
            
            self.type_label.setText("Type: -")
            self.uid_label.setText("UID: -")
            self.size_label.setText("Size: -")
            self.sectors_label.setText("Sectors: -")
            
            self.card_removed.emit()
    
    def refresh_card(self):
        """Refresh card information"""
        try:
            self.card_operations.detect_card()
            self.update_card_info()
        except Exception as e:
            logger.error(f"Error refreshing card: {e}")
