"""
Input validation utilities
"""

import re
from typing import Optional, Union, List

def validate_hex_key(key: str) -> tuple[bool, str]:
    """
    Validate hex key format for MIFARE authentication
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not key:
        return False, "Key cannot be empty"
    
    # Remove common separators
    clean_key = re.sub(r'[:\s-]', '', key.upper())
    
    # Check hex format
    if not re.match(r'^[0-9A-F]*$', clean_key):
        return False, "Key must contain only hex characters (0-9, A-F)"
    
    # Check length (6 bytes = 12 hex characters)
    if len(clean_key) != 12:
        return False, "Key must be exactly 6 bytes (12 hex characters)"
    
    return True, ""

def validate_block_number(block: int, card_type: int) -> tuple[bool, str]:
    """
    Validate block number for given card type
    
    Returns:
        tuple: (is_valid, error_message)
    """
    from config.constants import CARD_TYPE_MIFARE_1K, CARD_TYPE_MIFARE_4K
    
    if card_type == CARD_TYPE_MIFARE_1K:
        if 0 <= block <= 63:
            return True, ""
        else:
            return False, "Block number must be between 0 and 63 for MIFARE 1K"
    elif card_type == CARD_TYPE_MIFARE_4K:
        if 0 <= block <= 255:
            return True, ""
        else:
            return False, "Block number must be between 0 and 255 for MIFARE 4K"
    else:
        return False, "Unknown card type"

def validate_sector_number(sector: int, card_type: int) -> tuple[bool, str]:
    """
    Validate sector number for given card type
    
    Returns:
        tuple: (is_valid, error_message)
    """
    from config.constants import CARD_TYPE_MIFARE_1K, CARD_TYPE_MIFARE_4K
    
    if card_type == CARD_TYPE_MIFARE_1K:
        if 0 <= sector <= 15:
            return True, ""
        else:
            return False, "Sector number must be between 0 and 15 for MIFARE 1K"
    elif card_type == CARD_TYPE_MIFARE_4K:
        if 0 <= sector <= 39:
            return True, ""
        else:
            return False, "Sector number must be between 0 and 39 for MIFARE 4K"
    else:
        return False, "Unknown card type"

def validate_write_data(data: str) -> tuple[bool, str]:
    """
    Validate write data format (16 bytes)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "Write data cannot be empty"
    
    # Remove common separators
    clean_data = re.sub(r'[:\s-]', '', data.upper())
    
    # Check hex format
    if not re.match(r'^[0-9A-F]*$', clean_data):
        return False, "Data must contain only hex characters (0-9, A-F)"
    
    # Check length (16 bytes = 32 hex characters)
    if len(clean_data) != 32:
        return False, "Data must be exactly 16 bytes (32 hex characters)"
    
    return True, ""

def validate_access_conditions(access: str) -> tuple[bool, str]:
    """
    Validate access conditions format (3 bytes)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not access:
        return False, "Access conditions cannot be empty"
    
    # Remove common separators
    clean_access = re.sub(r'[:\s-]', '', access.upper())
    
    # Check hex format
    if not re.match(r'^[0-9A-F]*$', clean_access):
        return False, "Access conditions must contain only hex characters (0-9, A-F)"
    
    # Check length (3 bytes = 6 hex characters)
    if len(clean_access) != 6:
        return False, "Access conditions must be exactly 3 bytes (6 hex characters)"
    
    return True, ""
