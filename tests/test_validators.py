"""
Tests for validation utilities
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validators import (
    validate_hex_key, validate_block_number, validate_sector_number,
    validate_write_data, validate_access_conditions
)
from config.constants import CARD_TYPE_MIFARE_1K, CARD_TYPE_MIFARE_4K

class TestValidators(unittest.TestCase):
    """Test cases for validation utilities"""
    
    def test_validate_hex_key(self):
        """Test hex key validation"""
        # Valid keys
        valid_keys = [
            "FFFFFFFFFFFF",
            "FF FF FF FF FF FF",
            "A0:B1:C2:D3:E4:F5",
            "a0b1c2d3e4f5",
            "00 11 22 33 44 55"
        ]
        
        for key in valid_keys:
            is_valid, message = validate_hex_key(key)
            self.assertTrue(is_valid, f"Key {key} should be valid: {message}")
        
        # Invalid keys
        invalid_keys = [
            "",  # Empty
            "FFFFFFFFFF",  # Too short
            "FFFFFFFFFFFFFF",  # Too long
            "GGFFFFFFFFFFFF",  # Invalid hex
            "FF FF FF FF FF",  # Too short with spaces
        ]
        
        for key in invalid_keys:
            is_valid, message = validate_hex_key(key)
            self.assertFalse(is_valid, f"Key {key} should be invalid")
            self.assertIsInstance(message, str)
            self.assertGreater(len(message), 0)
    
    def test_validate_block_number(self):
        """Test block number validation"""
        # MIFARE 1K tests
        valid_1k_blocks = [0, 32, 63]
        for block in valid_1k_blocks:
            is_valid, message = validate_block_number(block, CARD_TYPE_MIFARE_1K)
            self.assertTrue(is_valid, f"Block {block} should be valid for 1K")
        
        invalid_1k_blocks = [-1, 64, 100]
        for block in invalid_1k_blocks:
            is_valid, message = validate_block_number(block, CARD_TYPE_MIFARE_1K)
            self.assertFalse(is_valid, f"Block {block} should be invalid for 1K")
        
        # MIFARE 4K tests
        valid_4k_blocks = [0, 128, 255]
        for block in valid_4k_blocks:
            is_valid, message = validate_block_number(block, CARD_TYPE_MIFARE_4K)
            self.assertTrue(is_valid, f"Block {block} should be valid for 4K")
        
        invalid_4k_blocks = [-1, 256, 300]
        for block in invalid_4k_blocks:
            is_valid, message = validate_block_number(block, CARD_TYPE_MIFARE_4K)
            self.assertFalse(is_valid, f"Block {block} should be invalid for 4K")
    
    def test_validate_write_data(self):
        """Test write data validation"""
        # Valid data (16 bytes = 32 hex chars)
        valid_data = [
            "00112233445566778899AABBCCDDEEFF",
            "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF",
            "00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff"
        ]
        
        for data in valid_data:
            is_valid, message = validate_write_data(data)
            self.assertTrue(is_valid, f"Data {data} should be valid: {message}")
        
        # Invalid data
        invalid_data = [
            "",  # Empty
            "001122334455667788",  # Too short
            "00112233445566778899AABBCCDDEEFF00",  # Too long
            "GG112233445566778899AABBCCDDEEFF",  # Invalid hex
        ]
        
        for data in invalid_data:
            is_valid, message = validate_write_data(data)
            self.assertFalse(is_valid, f"Data {data} should be invalid")

if __name__ == '__main__':
    unittest.main()
