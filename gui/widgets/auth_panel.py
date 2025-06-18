"""
Authentication panel for MIFARE Classic operations
"""

import logging
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QLineEdit, QCheckBox,
    QSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config.constants import KEY_TYPE_A, KEY_TYPE_B, KEY_TYPE_NAMES
from core.authentication import AuthenticationManager
from core.card_operations import CardOperations
from core.data_utils import is_valid_hex_string

logger = logging.getLogger(__name__)

class AuthPanel(QGroupBox):
    """Authentication panel widget"""
    
    authentication_success = pyqtSignal(int)  # sector
    authentication_failed = pyqtSignal(int)   # sector
    
    def __init__(self, auth_manager: AuthenticationManager, card_operations: CardOperations):
        super().__init__("Authentication")
        self.auth_manager = auth_manager
        self.card_operations = card_operations
        self.setup_ui()
        self.update_ui_state()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Sector selection
        sector_layout = QHBoxLayout()
        sector_layout.addWidget(QLabel("Sector:"))
        
        self.sector_spinbox = QSpinBox()
        self.sector_spinbox.setMinimum(0)
        self.sector_spinbox.setMaximum(15)  # Will be updated based on card type
        sector_layout.addWidget(self.sector_spinbox)
        
        sector_layout.addStretch()
        layout.addLayout(sector_layout)
        
        # Key type selection
        key_type_layout = QHBoxLayout()
        key_type_layout.addWidget(QLabel("Key Type:"))
        
        self.key_type_combo = QComboBox()
        self.key_type_combo.addItem("Key A", KEY_TYPE_A)
        self.key_type_combo.addItem("Key B", KEY_TYPE_B)
        key_type_layout.addWidget(self.key_type_combo)
        
        key_type_layout.addStretch()
        layout.addLayout(key_type_layout)
        
        # Key input
        key_layout = QVBoxLayout()
        key_layout.addWidget(QLabel("Authentication Key:"))
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter 6-byte key (12 hex characters)")
        self.key_input.setFont(QFont("Courier", 9))
        self.key_input.setMaxLength(17)  # 12 chars + spaces
        self.key_input.textChanged.connect(self.validate_key_input)
        key_layout.addWidget(self.key_input)
        
        layout.addLayout(key_layout)
        
        # Default key checkbox
        self.default_key_checkbox = QCheckBox("Use default key (FF FF FF FF FF FF)")
        self.default_key_checkbox.toggled.connect(self.on_default_key_toggled)
        layout.addWidget(self.default_key_checkbox)
        
        # Authentication buttons
        button_layout = QHBoxLayout()
        
        self.auth_button = QPushButton("Authenticate")
        self.auth_button.clicked.connect(self.authenticate)
        self.auth_button.setEnabled(False)
        button_layout.addWidget(self.auth_button)
        
        self.try_defaults_button = QPushButton("Try Default Keys")
        self.try_defaults_button.clicked.connect(self.try_default_keys)
        self.try_defaults_button.setEnabled(False)
        button_layout.addWidget(self.try_defaults_button)
        
        layout.addLayout(button_layout)
        
        # Authentication status
        self.status_label = QLabel("Not authenticated")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)
    
    def update_ui_state(self):
        """Update UI state based on card and reader status"""
        card_info = self.card_operations.get_card_info()
        reader_connected = self.card_operations.reader_manager.is_connected()
        
        # Update sector range based on card type
        if card_info.present:
            max_sector = card_info.get_sector_count() - 1
            self.sector_spinbox.setMaximum(max_sector)
        else:
            self.sector_spinbox.setMaximum(15)  # Default for 1K
        
        # Enable/disable controls
        controls_enabled = reader_connected and card_info.present
        self.sector_spinbox.setEnabled(controls_enabled)
        self.key_type_combo.setEnabled(controls_enabled)
        self.key_input.setEnabled(controls_enabled and not self.default_key_checkbox.isChecked())
        self.default_key_checkbox.setEnabled(controls_enabled)
        self.try_defaults_button.setEnabled(controls_enabled)
        
        # Update authenticate button
        self.update_auth_button_state()
        
        # Update status
        if controls_enabled:
            sector = self.sector_spinbox.value()
            if self.card_operations.is_sector_authenticated(sector):
                self.status_label.setText(f"Sector {sector} authenticated")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText("Not authenticated")
                self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setText("Not authenticated")
            self.status_label.setStyleSheet("color: red;")
    
    def validate_key_input(self):
        """Validate key input format"""
        if self.default_key_checkbox.isChecked():
            return
        
        text = self.key_input.text()
        if text and not is_valid_hex_string(text, 6):
            self.key_input.setStyleSheet("background-color: #ffcccc;")
        else:
            self.key_input.setStyleSheet("")
        
        self.update_auth_button_state()
    
    def update_auth_button_state(self):
        """Update authenticate button enabled state"""
        card_info = self.card_operations.get_card_info()
        reader_connected = self.card_operations.reader_manager.is_connected()
        
        if not (reader_connected and card_info.present):
            self.auth_button.setEnabled(False)
            return
        
        if self.default_key_checkbox.isChecked():
            self.auth_button.setEnabled(True)
        else:
            key_valid = is_valid_hex_string(self.key_input.text(), 6)
            self.auth_button.setEnabled(key_valid)
    
    def on_default_key_toggled(self, checked):
        """Handle default key checkbox toggle"""
        self.key_input.setEnabled(not checked)
        if checked:
            self.key_input.setText("FF FF FF FF FF FF")
        else:
            self.key_input.clear()
        
        self.update_auth_button_state()
    
    def authenticate(self):
        """Perform authentication"""
        try:
            sector = self.sector_spinbox.value()
            key_type = self.key_type_combo.currentData()
            
            if self.default_key_checkbox.isChecked():
                key_hex = "FFFFFFFFFFFF"
            else:
                key_hex = self.key_input.text().replace(" ", "")
            
            success = self.auth_manager.authenticate_with_key(sector, key_type, key_hex)
            
            if success:
                self.authentication_success.emit(sector)
                self.status_label.setText(f"Sector {sector} authenticated")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.authentication_failed.emit(sector)
                self.status_label.setText("Authentication failed")
                self.status_label.setStyleSheet("color: red;")
                QMessageBox.warning(self, "Authentication Failed", 
                                  f"Failed to authenticate sector {sector} with the provided key.")
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            QMessageBox.critical(self, "Error", f"Authentication error: {e}")
    
    def try_default_keys(self):
        """Try authentication with common default keys"""
        try:
            sector = self.sector_spinbox.value()
            key_type = self.key_type_combo.currentData()
            
            success = self.auth_manager.try_default_keys(sector, key_type)
            
            if success:
                self.authentication_success.emit(sector)
                self.status_label.setText(f"Sector {sector} authenticated (default key)")
                self.status_label.setStyleSheet("color: green;")
                QMessageBox.information(self, "Success", 
                                      f"Sector {sector} authenticated with a default key.")
            else:
                self.authentication_failed.emit(sector)
                self.status_label.setText("Authentication failed")
                self.status_label.setStyleSheet("color: red;")
                QMessageBox.warning(self, "Authentication Failed", 
                                  f"None of the default keys worked for sector {sector}.")
            
        except Exception as e:
            logger.error(f"Default key authentication error: {e}")
            QMessageBox.critical(self, "Error", f"Authentication error: {e}")
