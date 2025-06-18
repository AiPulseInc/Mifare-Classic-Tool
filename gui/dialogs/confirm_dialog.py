"""
Confirmation dialog for dangerous operations
"""

from PyQt5.QtWidgets import QMessageBox, QCheckBox, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class ConfirmDialog(QMessageBox):
    """Enhanced confirmation dialog with additional safety features"""
    
    def __init__(self, title, message, dangerous=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Warning if dangerous else QMessageBox.Question)
        
        if dangerous:
            # Add extra confirmation for dangerous operations
            self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            self.setDefaultButton(QMessageBox.No)
            
            # Add checkbox for additional confirmation
            self.checkbox = QCheckBox("I understand this operation cannot be undone")
            
            # Create layout with checkbox
            layout = self.layout()
            widget = QWidget()
            checkbox_layout = QVBoxLayout(widget)
            checkbox_layout.addWidget(self.checkbox)
            layout.addWidget(widget, 1, 1)
        else:
            self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            self.checkbox = None
    
    def exec_(self):
        """Execute dialog with additional validation for dangerous operations"""
        result = super().exec_()
        
        if result == QMessageBox.Yes and self.checkbox:
            if not self.checkbox.isChecked():
                QMessageBox.warning(self, "Confirmation Required", 
                                  "Please confirm you understand the risks by checking the box.")
                return QMessageBox.No
        
        return result
