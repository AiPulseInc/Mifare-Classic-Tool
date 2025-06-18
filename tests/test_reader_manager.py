"""
Tests for ReaderManager class
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reader_manager import ReaderManager, ReaderStatus

class TestReaderManager(unittest.TestCase):
    """Test cases for ReaderManager"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.reader_manager = ReaderManager()
    
    def tearDown(self):
        """Clean up after tests"""
        if self.reader_manager.is_connected():
            self.reader_manager.disconnect()
    
    def test_initial_status(self):
        """Test initial reader status"""
        self.assertEqual(self.reader_manager.status, ReaderStatus.DISCONNECTED)
        self.assertFalse(self.reader_manager.is_connected())
        self.assertIsNone(self.reader_manager.reader)
        self.assertIsNone(self.reader_manager.connection)
    
    @patch('core.reader_manager.readers')
    def test_get_available_readers(self, mock_readers):
        """Test getting available readers"""
        # Mock reader list
        mock_reader1 = Mock()
        mock_reader1.__str__ = Mock(return_value="ACS ACR1252 1S CL Reader PICC 0")
        mock_reader2 = Mock()
        mock_reader2.__str__ = Mock(return_value="Generic Reader")
        
        mock_readers.return_value = [mock_reader1, mock_reader2]
        
        readers = self.reader_manager.get_available_readers()
        
        self.assertEqual(len(readers), 2)
        self.assertIn("ACS ACR1252", readers[0])
        self.assertEqual(readers[1], "Generic Reader")
    
    @patch('core.reader_manager.readers')
    def test_find_acr1252u_reader(self, mock_readers):
        """Test finding ACR1252U reader"""
        # Mock reader list with ACR1252U
        mock_reader1 = Mock()
        mock_reader1.__str__ = Mock(return_value="ACS ACR1252 1S CL Reader PICC 0")
        mock_reader2 = Mock()
        mock_reader2.__str__ = Mock(return_value="Generic Reader")
        
        mock_readers.return_value = [mock_reader1, mock_reader2]
        
        found_reader = self.reader_manager.find_acr1252u_reader()
        
        self.assertIsNotNone(found_reader)
        self.assertIn("ACR1252", found_reader)
    
    def test_status_callbacks(self):
        """Test status change callbacks"""
        callback_mock = Mock()
        
        self.reader_manager.add_status_callback(callback_mock)
        self.reader_manager._notify_status_change(ReaderStatus.CONNECTING)
        
        callback_mock.assert_called_once_with(ReaderStatus.CONNECTING)
        self.assertEqual(self.reader_manager.status, ReaderStatus.CONNECTING)
        
        # Test removing callback
        self.reader_manager.remove_status_callback(callback_mock)
        self.reader_manager._notify_status_change(ReaderStatus.CONNECTED)
        
        # Should not be called again
        callback_mock.assert_called_once_with(ReaderStatus.CONNECTING)

if __name__ == '__main__':
    unittest.main()
