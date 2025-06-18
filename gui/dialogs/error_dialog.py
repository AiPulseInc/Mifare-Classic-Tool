"""
Error dialog for displaying error messages
"""

from PyQt5.QtWidgets import QMessageBox, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ErrorDialog(QMessageBox):
    """Enhanced error dialog with details expansion"""
    
    def __init__(self, title, message, details=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Critical)
        self.setStandardButtons(QMessageBox.Ok)
        
        if details:
            self.setDetailedText(details)
            
            # Customize detailed text widget
            for widget in self.findChildren(QTextEdit):
                widget.setFont(QFont("Courier", 8))
                widget.setMinimumWidth(500)
                widget.setMinimumHeight(200)

def show_error(title, message, details=None, parent=None):
    """Convenience function to show error dialog"""
    dialog = ErrorDialog(title, message, details, parent)
    return dialog.exec_()

def show_warning(title, message, parent=None):
    """Convenience function to show warning dialog"""
    return QMessageBox.warning(parent, title, message, 
                             QMessageBox.Ok, QMessageBox.Ok)

def show_info(title, message, parent=None):
    """Convenience function to show info dialog"""
    return QMessageBox.information(parent, title, message, 
                                 QMessageBox.Ok, QMessageBox.Ok)

def confirm_dangerous_operation(title, message, parent=None):
    """Convenience function for dangerous operation confirmation"""
    dialog = ConfirmDialog(title, message, dangerous=True, parent=parent)
    return dialog.exec_() == QMessageBox.Yes
