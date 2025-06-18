"""
Data formatting utilities
"""

from typing import List, Optional, Union
import binascii

def format_hex_string(data: Union[str, bytes], separator: str = " ", uppercase: bool = True) -> str:
    """Format hex string with consistent spacing and case"""
    if isinstance(data, bytes):
        hex_str = data.hex()
    else:
        hex_str = data.replace(" ", "").replace(":", "").replace("-", "")
    
    if uppercase:
        hex_str = hex_str.upper()
    else:
        hex_str = hex_str.lower()
    
    # Add separators every 2 characters
    if separator:
        return separator.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
    
    return hex_str

def format_block_display(block_number: int, data: bytes, show_ascii: bool = True) -> str:
    """Format block data for display with block number"""
    hex_data = format_hex_string(data)
    
    if not show_ascii:
        return f"Block {block_number:02d}: {hex_data}"
    
    # Add ASCII representation
    ascii_str = ""
    for b in data:
        if 32 <= b <= 126:  # Printable ASCII
            ascii_str += chr(b)
        else:
            ascii_str += "."
    
    return f"Block {block_number:02d}: {hex_data} | {ascii_str}"

def format_sector_info(sector: int, card_type: int) -> str:
    """Format sector information"""
    from config.constants import CARD_TYPE_MIFARE_1K, CARD_TYPE_MIFARE_4K
    
    if card_type == CARD_TYPE_MIFARE_1K:
        start_block = sector * 4
        end_block = start_block + 3
        return f"Sector {sector}: Blocks {start_block}-{end_block}"
    elif card_type == CARD_TYPE_MIFARE_4K:
        if sector < 32:
            start_block = sector * 4
            end_block = start_block + 3
        else:
            start_block = 32 * 4 + (sector - 32) * 16
            end_block = start_block + 15
        return f"Sector {sector}: Blocks {start_block}-{end_block}"
    
    return f"Sector {sector}: Unknown layout"

def format_key_display(key: bytes, mask: bool = True) -> str:
    """Format key for display with optional masking"""
    if mask:
        return "XX XX XX XX XX XX"
    else:
        return format_hex_string(key)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
