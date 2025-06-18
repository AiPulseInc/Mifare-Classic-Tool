"""
Block operations panel for read/write operations
"""

import logging
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QTextEdit, QComboBox,
    QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from core.card_operations import CardOperations
from core.authentication import AuthenticationManager
from core.data_utils import (
    bytes_to_hex_string, hex_string_to_bytes, 
    format_block_data, is_valid_hex_string
)

logger = logging.getLogger(__name__)

class BlockPanel(QGroupBox):
    """Block operations panel widget"""
    
    operation_completed = pyqtSignal(str, bool)  # operation, success
    
    def __init__(self, card_operations: CardOperations, auth_manager: AuthenticationManager):
        super().__init__("Block Operations")
        self.card_operations = card_operations
        self.auth_manager = auth_manager
        self.setup_ui()
        self.update_ui_state()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Block selection
        block_layout = QHBoxLayout()
        block_layout.addWidget(QLabel("Block:"))
        
        self.block_spinbox = QSpinBox()
        self.block_spinbox.setMinimum(0)
        self.block_spinbox.setMaximum(63)
        self.block_spinbox.valueChanged.connect(self.on_block_changed)
        block_layout.addWidget(self.block_spinbox)
        
        self.block_info_label = QLabel()
        self.block_info_label.setStyleSheet("color: blue;")
        block_layout.addWidget(self.block_info_label)
        
        block_layout.addStretch()
        layout.addLayout(block_layout)
        
        # Read operations
        read_layout = QHBoxLayout()
        
        self.read_button = QPushButton("Read Block")
        self.read_button.clicked.connect(self.read_block)
        self.read_button.setEnabled(False)
        read_layout.addWidget(self.read_button)
        
        self.auto_read_checkbox = QCheckBox("Auto-read on block change")
        read_layout.addWidget(self.auto_read_checkbox)
        
        read_layout.addStretch()
        layout.addLayout(read_layout)
        
        # Data display
        layout.addWidget(QLabel("Block Data:"))
        
        self.data_display = QTextEdit()
        self.data_display.setFont(QFont("Courier", 9))
        self.data_display.setMaximumHeight(100)
        self.data_display.setReadOnly(True)
        layout.addWidget(self.data_display)
        
        # Write operations
        layout.addWidget(QLabel("Write Data (32 hex characters):"))
        
        self.write_input = QTextEdit()
        self.write_input.setFont(QFont("Courier", 9))
        self.write_input.setMaximumHeight(60)
        self.write_input.setPlaceholderText("Enter 16 bytes as hex")
        self.write_input.textChanged.connect(self.validate_write_input)
        layout.addWidget(self.write_input)
        
        # Write controls
        write_control_layout = QHBoxLayout()
        
        self.write_button = QPushButton("Write Block")
        self.write_button.clicked.connect(self.write_block)
        self.write_button.setEnabled(False)
        write_control_layout.addWidget(self.write_button)
        
        self.clear_input_button = QPushButton("Clear")
        self.clear_input_button.clicked.connect(self.clear_write_input)
        write_control_layout.addWidget(self.clear_input_button)
        
        write_control_layout.addStretch()
        layout.addLayout(write_control_layout)
        
        self.current_block_data = None
    
    def update_ui_state(self):
        """Update UI state based on card and authentication status"""
        card_info = self.card_operations.get_card_info()
        reader_connected = self.card_operations.reader_manager.is_connected()
        
        if card_info.present:
            max_block = card_info.get_block_count() - 1
            self.block_spinbox.setMaximum(max_block)
        else:
            self.block_spinbox.setMaximum(63)
        
        self.update_block_info()
        
        controls_enabled = reader_connected and card_info.present
        block_accessible = self.is_current_block_accessible()
        
        self.block_spinbox.setEnabled(controls_enabled)
        self.read_button.setEnabled(controls_enabled and block_accessible)
        self.write_button.setEnabled(controls_enabled and block_accessible and self.is_write_data_valid())
        
        if (self.auto_read_checkbox.isChecked() and 
            controls_enabled and block_accessible):
            self.read_block()
    
    def update_block_info(self):
        """Update block information display"""
        card_info = self.card_operations.get_card_info()
        current_block = self.block_spinbox.value()
        
        if not card_info.present:
            self.block_info_label.setText("")
            return
        
        if card_info.is_trailer_block(current_block):
            self.block_info_label.setText("(Trailer Block)")
            self.block_info_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            sector = self._get_sector_from_block(current_block)
            self.block_info_label.setText(f"(Sector {sector})")
            self.block_info_label.setStyleSheet("color: blue;")
    
    def on_block_changed(self):
        """Handle block number change"""
        self.update_block_info()
        self.update_ui_state()
        self.current_block_data = None
        self.data_display.clear()
    
    def is_current_block_accessible(self):
        """Check if current block is accessible"""
        current_block = self.block_spinbox.value()
        sector = self._get_sector_from_block(current_block)
        return self.card_operations.is_sector_authenticated(sector)
    
    def _get_sector_from_block(self, block_number):
        """Get sector number from block number"""
        card_info = self.card_operations.get_card_info()
        if card_info.card_type == 1:  # MIFARE 1K
            return block_number // 4
        elif card_info.card_type == 2:  # MIFARE 4K
            if block_number < 32 * 4:
                return block_number // 4
            else:
                return 32 + (block_number - 32 * 4) // 16
        return 0
    
    def read_block(self):
        """Read current block"""
        try:
            current_block = self.block_spinbox.value()
            
            self.current_block_data = self.card_operations.read_block(current_block)
            
            if self.current_block_data:
                formatted_data = format_block_data(self.current_block_data, True)
                self.data_display.setText(formatted_data)
                self.operation_completed.emit(f"Read block {current_block}", True)
                logger.info(f"Successfully read block {current_block}")
            else:
                self.data_display.setText("Read failed")
                self.operation_completed.emit(f"Read block {current_block}", False)
                QMessageBox.warning(self, "Read Failed", 
                                  f"Failed to read block {current_block}.")
            
        except Exception as e:
            logger.error(f"Error reading block: {e}")
            self.operation_completed.emit("Read block", False)
            QMessageBox.critical(self, "Error", f"Error reading block: {e}")
    
    def validate_write_input(self):
        """Validate write input data"""
        text = self.write_input.toPlainText()
        
        if not text:
            self.write_input.setStyleSheet("")
            self.write_button.setEnabled(False)
            return
        
        if is_valid_hex_string(text, 16):
            self.write_input.setStyleSheet("")
        else:
            self.write_input.setStyleSheet("background-color: #ffcccc;")
        
        self.update_ui_state()
    
    def is_write_data_valid(self):
        """Check if write data is valid"""
        text = self.write_input.toPlainText()
        return is_valid_hex_string(text, 16)
    
    def write_block(self):
        """Write data to current block"""
        try:
            current_block = self.block_spinbox.value()
            card_info = self.card_operations.get_card_info()
            
            # Confirm if writing to trailer block
            if card_info.is_trailer_block(current_block):
                reply = QMessageBox.question(
                    self, "Confirm Write", 
                    f"Block {current_block} is a trailer block containing access keys and conditions.\\n"
                    "Writing incorrect data may permanently lock the sector!\\n\\n"
                    "Are you sure you want to continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return
            
            # Get write data
            hex_text = self.write_input.toPlainText()
            write_data = hex_string_to_bytes(hex_text)
            
            if write_data is None or len(write_data) != 16:
                QMessageBox.warning(self, "Invalid Data", "Write data must be exactly 16 bytes (32 hex characters).")
                return
            
            # Perform write
            success = self.card_operations.write_block(current_block, write_data)
            
            if success:
                self.operation_completed.emit(f"Write block {current_block}", True)
                QMessageBox.information(self, "Success", f"Block {current_block} written successfully.")
                self.read_block()  # Auto-read to verify
            else:
                self.operation_completed.emit(f"Write block {current_block}", False)
                QMessageBox.warning(self, "Write Failed", f"Failed to write block {current_block}.")
            
        except Exception as e:
            logger.error(f"Error writing block: {e}")
            self.operation_completed.emit("Write block", False)
            QMessageBox.critical(self, "Error", f"Error writing block: {e}")
    
    def clear_write_input(self):
        """Clear write input field"""
        self.write_input.clear()
