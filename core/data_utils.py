"""
Data utilities for MIFARE Classic Tool
Handles data conversion, validation, and formatting
"""

import re
from typing import Optional, List, Union

def bytes_to_hex_string(data: bytes, separator: str = " ") -> str:
    """Convert bytes to hex string with optional separator"""
    return separator.join(f"{b:02X}" for b in data)

def hex_string_to_bytes(hex_str: str) -> Optional[bytes]:
    """Convert hex string to bytes, handling various formats"""
    try:
        # Remove common separators and whitespace
        clean_hex = re.sub(r'[:\s-]', '', hex_str.upper())
        
        # Validate hex characters
        if not re.match(r'^[0-9A-F]*$', clean_hex):
            return None
        
        # Must be even length
        if len(clean_hex) % 2 != 0:
            return None
        
        return bytes.fromhex(clean_hex)
    except ValueError:
        return None

def is_valid_hex_string(hex_str: str, expected_length: Optional[int] = None) -> bool:
    """Validate hex string format and optionally length"""
    if not hex_str:
        return False
    
    clean_hex = re.sub(r'[:\s-]', '', hex_str.upper())
    
    # Check hex format
    if not re.match(r'^[0-9A-F]*$', clean_hex):
        return False
    
    # Check length
    if len(clean_hex) % 2 != 0:
        return False
    
    if expected_length and len(clean_hex) != expected_length * 2:
        return False
    
    return True

def format_block_data(data: bytes, show_ascii: bool = True) -> str:
    """Format block data for display"""
    hex_str = bytes_to_hex_string(data)
    
    if not show_ascii:
        return hex_str
    
    # Add ASCII representation
    ascii_str = ""
    for b in data:
        if 32 <= b <= 126:  # Printable ASCII
            ascii_str += chr(b)
        else:
            ascii_str += "."
    
    return f"{hex_str} | {ascii_str}"

def validate_block_number(block_number: int, card_type: int) -> bool:
    """Validate block number for given card type"""
    from config.constants import CARD_TYPE_MIFARE_1K, CARD_TYPE_MIFARE_4K
    
    if card_type == CARD_TYPE_MIFARE_1K:
        return 0 <= block_number <= 63
    elif card_type == CARD_TYPE_MIFARE_4K:
        return 0 <= block_number <= 255
    
    return False

def validate_sector_number(sector: int, card_type: int) -> bool:
    """Validate sector number for given card type"""
    from config.constants import CARD_TYPE_MIFARE_1K, CARD_TYPE_MIFARE_4K
    
    if card_type == CARD_TYPE_MIFARE_1K:
        return 0 <= sector <= 15
    elif card_type == CARD_TYPE_MIFARE_4K:
        return 0 <= sector <= 39
    
    return False

def parse_access_bits(trailer_data: bytes) -> dict:
    """Parse access bits from trailer block"""
    if len(trailer_data) != 16:
        return {}
    
    # Access bits are at bytes 6, 7, 8
    access_bytes = trailer_data[6:9]
    
    # This is a simplified parser - full implementation would
    # decode the complex access bit structure
    return {
        "raw": bytes_to_hex_string(access_bytes),
        "c1": access_bytes[0],
        "c2": access_bytes[1], 
        "c3": access_bytes[2]
    }
