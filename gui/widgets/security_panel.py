"""
Security operations panel for advanced MIFARE operations
"""

import logging
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QLineEdit, QTextEdit,
    QMessageBox, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from core.card_operations import CardOperations
from core.authentication import AuthenticationManager
from core.data_utils import bytes_to_hex_string, hex_string_to_bytes, is_valid_hex_string

logger = logging.getLogger(__name__)

class SecurityPanel(QGroupBox):
    """Security operations panel widget"""
    
    def __init__(self, card_operations: CardOperations, auth_manager: AuthenticationManager):
        super().__init__("Security Operations")
        self.card_operations = card_operations
        self.auth_manager = auth_manager
        self.setup_ui()
        self.update_ui_state()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tabs for different security operations
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Trailer block operations tab
        self.setup_trailer_tab()
        
        # Key management tab
        self.setup_key_management_tab()
        
        # Access conditions tab
        self.setup_access_conditions_tab()
    
    def setup_trailer_tab(self):
        """Setup trailer block operations tab"""
        trailer_widget = QWidget()
        layout = QVBoxLayout(trailer_widget)
        
        # Sector selection
        sector_layout = QHBoxLayout()
        sector_layout.addWidget(QLabel("Sector:"))
        
        self.trailer_sector_spinbox = QSpinBox()
        self.trailer_sector_spinbox.setMinimum(0)
        self.trailer_sector_spinbox.setMaximum(15)
        self.trailer_sector_spinbox.valueChanged.connect(self.update_trailer_display)
        sector_layout.addWidget(self.trailer_sector_spinbox)
        
        sector_layout.addStretch()
        layout.addLayout(sector_layout)
        
        # Read trailer button
        self.read_trailer_button = QPushButton("Read Trailer Block")
        self.read_trailer_button.clicked.connect(self.read_trailer_block)
        self.read_trailer_button.setEnabled(False)
        layout.addWidget(self.read_trailer_button)
        
        # Trailer data display
        layout.addWidget(QLabel("Trailer Block Data:"))
        
        self.trailer_display = QTextEdit()
        self.trailer_display.setFont(QFont("Courier", 9))
        self.trailer_display.setMaximumHeight(120)
        self.trailer_display.setReadOnly(True)
        layout.addWidget(self.trailer_display)
        
        self.tabs.addTab(trailer_widget, "Trailer Blocks")
    
    def setup_key_management_tab(self):
        """Setup key management tab"""
        key_widget = QWidget()
        layout = QVBoxLayout(key_widget)
        
        layout.addWidget(QLabel("Key Management (Advanced - Use with caution!)"))
        
        # Sector selection for key operations
        sector_layout = QHBoxLayout()
        sector_layout.addWidget(QLabel("Sector:"))
        
        self.key_sector_spinbox = QSpinBox()
        self.key_sector_spinbox.setMinimum(0)
        self.key_sector_spinbox.setMaximum(15)
        sector_layout.addWidget(self.key_sector_spinbox)
        
        sector_layout.addStretch()
        layout.addLayout(sector_layout)
        
        # New Key A input
        layout.addWidget(QLabel("New Key A:"))
        self.new_key_a_input = QLineEdit()
        self.new_key_a_input.setPlaceholderText("Enter new Key A (12 hex characters)")
        self.new_key_a_input.setFont(QFont("Courier", 9))
        self.new_key_a_input.textChanged.connect(self.validate_key_inputs)
        layout.addWidget(self.new_key_a_input)
        
        # New Key B input
        layout.addWidget(QLabel("New Key B:"))
        self.new_key_b_input = QLineEdit()
        self.new_key_b_input.setPlaceholderText("Enter new Key B (12 hex characters)")
        self.new_key_b_input.setFont(QFont("Courier", 9))
        self.new_key_b_input.textChanged.connect(self.validate_key_inputs)
        layout.addWidget(self.new_key_b_input)
        
        # Access conditions input
        layout.addWidget(QLabel("Access Conditions (6 hex characters):"))
        self.access_conditions_input = QLineEdit()
        self.access_conditions_input.setPlaceholderText("Enter access conditions (e.g., FF0780)")
        self.access_conditions_input.setFont(QFont("Courier", 9))
        self.access_conditions_input.textChanged.connect(self.validate_key_inputs)
        layout.addWidget(self.access_conditions_input)
        
        # Update keys button
        self.update_keys_button = QPushButton("Update Sector Keys")
        self.update_keys_button.clicked.connect(self.update_sector_keys)
        self.update_keys_button.setEnabled(False)
        layout.addWidget(self.update_keys_button)
        
        # Warning label
        warning_label = QLabel("⚠️ WARNING: Incorrect key changes can permanently lock sectors!")
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(warning_label)
        
        layout.addStretch()
        self.tabs.addTab(key_widget, "Key Management")
    
    def setup_access_conditions_tab(self):
        """Setup access conditions tab"""
        access_widget = QWidget()
        layout = QVBoxLayout(access_widget)
        
        layout.addWidget(QLabel("Access Conditions Reference"))
        
        # Access conditions reference text
        reference_text = """
Common Access Conditions:

FF 07 80 69 - Transport Configuration (Key A: read/write, Key B: read/write)
78 77 88 C1 - Key A: read only, Key B: read/write  
FF 07 80 00 - Key A: read/write, Key B: read only
00 00 00 00 - Both keys: no access (lock sector permanently!)

Data Block Access:
- C1 C2 C3 combinations control read/write permissions
- 000: read/write with Key A or B
- 001: read with Key A or B, write with Key B
- 010: read with Key A or B, write never
- 011: read/write with Key B
- 100: read with Key A or B, write never  
- 101: read/write never
- 110: read with Key A or B, write with Key B
- 111: read/write never

Trailer Block Access:
- Controls key A/B read/write permissions
- Controls access condition bits modification
"""
        
        reference_display = QTextEdit()
        reference_display.setFont(QFont("Courier", 8))
        reference_display.setText(reference_text)
        reference_display.setReadOnly(True)
        layout.addWidget(reference_display)
        
        self.tabs.addTab(access_widget, "Access Reference")
    
    def update_ui_state(self):
        """Update UI state based on card and authentication status"""
        card_info = self.card_operations.get_card_info()
        reader_connected = self.card_operations.reader_manager.is_connected()
        
        # Update sector ranges
        if card_info.present:
            max_sector = card_info.get_sector_count() - 1
            self.trailer_sector_spinbox.setMaximum(max_sector)
            self.key_sector_spinbox.setMaximum(max_sector)
        
        # Enable/disable controls
        controls_enabled = reader_connected and card_info.present
        
        # Trailer operations
        current_sector = self.trailer_sector_spinbox.value()
        sector_authenticated = self.card_operations.is_sector_authenticated(current_sector)
        
        self.trailer_sector_spinbox.setEnabled(controls_enabled)
        self.read_trailer_button.setEnabled(controls_enabled and sector_authenticated)
        
        # Key management
        key_sector = self.key_sector_spinbox.value()
        key_sector_authenticated = self.card_operations.is_sector_authenticated(key_sector)
        keys_valid = self.are_key_inputs_valid()
        
        self.key_sector_spinbox.setEnabled(controls_enabled)
        self.new_key_a_input.setEnabled(controls_enabled)
        self.new_key_b_input.setEnabled(controls_enabled)
        self.access_conditions_input.setEnabled(controls_enabled)
        self.update_keys_button.setEnabled(controls_enabled and key_sector_authenticated and keys_valid)
    
    def update_trailer_display(self):
        """Update trailer block display"""
        self.trailer_display.clear()
        self.update_ui_state()
    
    def read_trailer_block(self):
        """Read and display trailer block"""
        try:
            sector = self.trailer_sector_spinbox.value()
            card_info = self.card_operations.get_card_info()
            
            trailer_block = card_info.get_trailer_block(sector)
            
            if trailer_block >= 0:
                data = self.card_operations.read_block(trailer_block)
                
                if data:
                    # Format trailer data with security masking
                    hex_data = bytes_to_hex_string(data)
                    
                    # Mask Key A (bytes 0-5) and Key B (bytes 10-15)
                    masked_data = list(data)
                    for i in range(6):  # Key A
                        masked_data[i] = 0xFF
                    for i in range(10, 16):  # Key B  
                        masked_data[i] = 0xFF
                    
                    masked_hex = bytes_to_hex_string(bytes(masked_data))
                    
                    display_text = f"Trailer Block {trailer_block} (Sector {sector}):\\n"
                    display_text += f"Raw Data: {hex_data}\\n"
                    display_text += f"Masked:   {masked_hex}\\n\\n"
                    display_text += f"Key A:     [MASKED]\\n"
                    display_text += f"Access:    {hex_data[18:24]}\\n"  # bytes 6-8
                    display_text += f"Key B:     [MASKED]\\n"
                    
                    self.trailer_display.setText(display_text)
                else:
                    self.trailer_display.setText("Failed to read trailer block")
            
        except Exception as e:
            logger.error(f"Error reading trailer block: {e}")
            QMessageBox.critical(self, "Error", f"Error reading trailer block: {e}")
    
    def validate_key_inputs(self):
        """Validate key management inputs"""
        key_a_valid = is_valid_hex_string(self.new_key_a_input.text(), 6)
        key_b_valid = is_valid_hex_string(self.new_key_b_input.text(), 6)
        access_valid = is_valid_hex_string(self.access_conditions_input.text(), 3)
        
        # Update input styling
        self.new_key_a_input.setStyleSheet("" if key_a_valid or not self.new_key_a_input.text() else "background-color: #ffcccc;")
        self.new_key_b_input.setStyleSheet("" if key_b_valid or not self.new_key_b_input.text() else "background-color: #ffcccc;")
        self.access_conditions_input.setStyleSheet("" if access_valid or not self.access_conditions_input.text() else "background-color: #ffcccc;")
        
        self.update_ui_state()
    
    def are_key_inputs_valid(self):
        """Check if all key inputs are valid"""
        key_a_valid = is_valid_hex_string(self.new_key_a_input.text(), 6)
        key_b_valid = is_valid_hex_string(self.new_key_b_input.text(), 6)
        access_valid = is_valid_hex_string(self.access_conditions_input.text(), 3)
        
        return (key_a_valid and key_b_valid and access_valid and 
                self.new_key_a_input.text() and 
                self.new_key_b_input.text() and
                self.access_conditions_input.text())
    
    def update_sector_keys(self):
        """Update sector keys and access conditions"""
        try:
            sector = self.key_sector_spinbox.value()
            
            # Multiple confirmation dialogs for safety
            reply1 = QMessageBox.question(
                self, "Confirm Key Change", 
                f"You are about to change keys and access conditions for sector {sector}.\\n\\n"
                "This operation is IRREVERSIBLE and may permanently lock the sector if done incorrectly!\\n\\n"
                "Are you absolutely sure you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply1 != QMessageBox.Yes:
                return
            
            reply2 = QMessageBox.question(
                self, "Final Confirmation", 
                f"FINAL WARNING!\\n\\n"
                f"Sector: {sector}\\n"
                f"New Key A: {self.new_key_a_input.text()}\\n"
                f"New Key B: {self.new_key_b_input.text()}\\n"
                f"Access: {self.access_conditions_input.text()}\\n\\n"
                "Proceed with key change?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply2 != QMessageBox.Yes:
                return
            
            # Get trailer block number
            card_info = self.card_operations.get_card_info()
            trailer_block = card_info.get_trailer_block(sector)
            
            if trailer_block < 0:
                QMessageBox.critical(self, "Error", "Invalid sector number")
                return
            
            # Construct new trailer data
            key_a = hex_string_to_bytes(self.new_key_a_input.text())
            key_b = hex_string_to_bytes(self.new_key_b_input.text())
            access_conditions = hex_string_to_bytes(self.access_conditions_input.text())
            
            if not all([key_a, key_b, access_conditions]):
                QMessageBox.critical(self, "Error", "Invalid key or access condition format")
                return
            
            # Build trailer data: Key A (6) + Access (3) + GPB (1) + Key B (6)
            trailer_data = key_a + access_conditions + bytes([0x69]) + key_b
            
            # Write trailer block
            success = self.card_operations.write_block(trailer_block, trailer_data)
            
            if success:
                QMessageBox.information(self, "Success", 
                                      f"Sector {sector} keys updated successfully.\\n\\n"
                                      "You will need to re-authenticate with the new keys.")
                
                # Clear authentication for this sector since keys changed
                self.card_operations.set_sector_authenticated(sector, False)
                
                # Clear input fields
                self.new_key_a_input.clear()
                self.new_key_b_input.clear()
                self.access_conditions_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to update sector keys")
            
        except Exception as e:
            logger.error(f"Error updating sector keys: {e}")
            QMessageBox.critical(self, "Error", f"Error updating sector keys: {e}")
