"""
MIFARE Classic Authentication Manager
Handles key loading and sector authentication
"""

import logging
from typing import Optional, List
from smartcard.Exceptions import CardConnectionException

from config.constants import (
    APDUCommands, ErrorCodes, KEY_TYPE_A, KEY_TYPE_B,
    DEFAULT_KEY, TRANSPORT_KEY
)
from .reader_manager import ReaderManager
from .card_operations import CardOperations

logger = logging.getLogger(__name__)

class AuthenticationManager:
    """Manages MIFARE Classic authentication operations"""
    
    def __init__(self, reader_manager: ReaderManager, card_operations: CardOperations):
        self.reader_manager = reader_manager
        self.card_operations = card_operations
        self._loaded_keys = {}  # key_slot -> key_data
    
    def load_key(self, key_data: bytes, key_slot: int = 0) -> bool:
        """Load authentication key into reader memory"""
        try:
            if len(key_data) != 6:
                raise ValueError("Key must be exactly 6 bytes")
            
            if not self.reader_manager.is_connected():
                raise CardConnectionException("Reader not connected")
            
            # Prepare load key command
            command = APDUCommands.LOAD_AUTH_KEY + [key_slot] + list(key_data)
            
            response, sw1, sw2 = self.reader_manager.send_apdu(command)
            
            if sw1 == 0x90 and sw2 == 0x00:
                self._loaded_keys[key_slot] = key_data
                logger.info(f"Key loaded into slot {key_slot}")
                return True
            else:
                logger.error(f"Failed to load key into slot {key_slot}: {sw1:02X}{sw2:02X}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading key: {e}")
            return False
    
    def authenticate_sector(self, sector: int, key_type: int, key_data: bytes, key_slot: int = 0) -> bool:
        """Authenticate sector with specified key"""
        try:
            if not self.card_operations.card_info.present:
                raise CardConnectionException("No card present")
            
            # Load key first
            if not self.load_key(key_data, key_slot):
                return False
            
            # Get block number for authentication (any block in sector)
            if self.card_operations.card_info.card_type == 1:  # MIFARE 1K
                block_number = sector * 4
            else:  # MIFARE 4K
                if sector < 32:
                    block_number = sector * 4
                else:
                    block_number = 32 * 4 + (sector - 32) * 16
            
            # Prepare authentication command
            auth_data = [0x01, 0x00, block_number, key_type, key_slot]
            command = APDUCommands.AUTH_BLOCK + auth_data
            
            response, sw1, sw2 = self.reader_manager.send_apdu(command)
            
            if sw1 == 0x90 and sw2 == 0x00:
                self.card_operations.set_sector_authenticated(sector, True)
                logger.info(f"Sector {sector} authenticated with key type {key_type:02X}")
                return True
            else:
                logger.error(f"Authentication failed for sector {sector}: {sw1:02X}{sw2:02X}")
                return False
                
        except Exception as e:
            logger.error(f"Error authenticating sector {sector}: {e}")
            return False
    
    def try_default_keys(self, sector: int, key_type: int) -> bool:
        """Try common default keys for authentication"""
        default_keys = [
            DEFAULT_KEY,
            TRANSPORT_KEY,
            bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # All zeros
            bytes([0xA0, 0xB0, 0xC0, 0xD0, 0xE0, 0xF0]),  # Another common key
        ]
        
        for i, key in enumerate(default_keys):
            logger.debug(f"Trying default key {i+1}/{len(default_keys)} for sector {sector}")
            if self.authenticate_sector(sector, key_type, key):
                logger.info(f"Sector {sector} authenticated with default key {i+1}")
                return True
        
        logger.warning(f"No default keys worked for sector {sector}")
        return False
    
    def authenticate_with_key(self, sector: int, key_type: int, key_hex: str) -> bool:
        """Authenticate with hex key string"""
        try:
            # Convert hex string to bytes
            key_hex = key_hex.replace(" ", "").replace(":", "")
            if len(key_hex) != 12:
                raise ValueError("Key must be 12 hex characters (6 bytes)")
            
            key_bytes = bytes.fromhex(key_hex)
            return self.authenticate_sector(sector, key_type, key_bytes)
            
        except ValueError as e:
            logger.error(f"Invalid key format: {e}")
            return False
    
    def clear_loaded_keys(self) -> None:
        """Clear all loaded keys from memory"""
        self._loaded_keys.clear()
        self.card_operations.clear_authentication()
        logger.debug("Cleared all loaded keys and authentication states")
