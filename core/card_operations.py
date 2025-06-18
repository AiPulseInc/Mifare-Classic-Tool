"""
MIFARE Classic Card Operations
Handles card detection, reading, and writing operations
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from smartcard.Exceptions import NoCardException, CardConnectionException

from config.constants import (
    APDUCommands, ErrorCodes, CARD_TYPE_MIFARE_1K, CARD_TYPE_MIFARE_4K,
    CARD_TYPE_UNKNOWN, MIFARE_BLOCK_SIZE, MIFARE_1K_SECTORS, MIFARE_4K_SECTORS
)
from .reader_manager import ReaderManager

logger = logging.getLogger(__name__)

class CardInfo:
    """Card information container"""
    
    def __init__(self):
        self.uid: Optional[bytes] = None
        self.card_type: int = CARD_TYPE_UNKNOWN
        self.size: int = 0
        self.sectors: int = 0
        self.present: bool = False
    
    def get_card_type_name(self) -> str:
        """Get human-readable card type name"""
        from config.constants import CARD_TYPE_NAMES
        return CARD_TYPE_NAMES.get(self.card_type, "Unknown")
    
    def get_sector_count(self) -> int:
        """Get number of sectors based on card type"""
        if self.card_type == CARD_TYPE_MIFARE_1K:
            return MIFARE_1K_SECTORS
        elif self.card_type == CARD_TYPE_MIFARE_4K:
            return MIFARE_4K_SECTORS
        return 0
    
    def get_block_count(self) -> int:
        """Get total number of blocks"""
        if self.card_type == CARD_TYPE_MIFARE_1K:
            return 64  # 16 sectors * 4 blocks
        elif self.card_type == CARD_TYPE_MIFARE_4K:
            # 32 sectors * 4 blocks + 8 sectors * 16 blocks
            return 32 * 4 + 8 * 16
        return 0
    
    def get_trailer_block(self, sector: int) -> int:
        """Get trailer block number for given sector"""
        if self.card_type == CARD_TYPE_MIFARE_1K:
            return sector * 4 + 3
        elif self.card_type == CARD_TYPE_MIFARE_4K:
            if sector < 32:
                return sector * 4 + 3
            else:
                return 32 * 4 + (sector - 32) * 16 + 15
        return -1
    
    def is_trailer_block(self, block: int) -> bool:
        """Check if block is a trailer block"""
        if self.card_type == CARD_TYPE_MIFARE_1K:
            return (block + 1) % 4 == 0
        elif self.card_type == CARD_TYPE_MIFARE_4K:
            if block < 32 * 4:  # First 32 sectors
                return (block + 1) % 4 == 0
            else:  # Last 8 sectors
                relative_block = block - 32 * 4
                return (relative_block + 1) % 16 == 0
        return False

class CardOperations:
    """Handles MIFARE Classic card operations"""
    
    def __init__(self, reader_manager: ReaderManager):
        self.reader_manager = reader_manager
        self.card_info = CardInfo()
        self._authenticated_sectors: Dict[int, bool] = {}
    
    def detect_card(self) -> bool:
        """Detect if a MIFARE Classic card is present"""
        try:
            if not self.reader_manager.is_connected():
                self.card_info.present = False
                return False
            
            # Try to get UID
            response, sw1, sw2 = self.reader_manager.send_apdu(APDUCommands.GET_UID)
            
            if sw1 == 0x90 and sw2 == 0x00 and len(response) > 0:
                self.card_info.uid = bytes(response)
                self.card_info.present = True
                
                # Determine card type based on UID length and other factors
                self._determine_card_type()
                
                logger.info(f"Card detected: UID={self.card_info.uid.hex()}, Type={self.card_info.get_card_type_name()}")
                return True
            else:
                self.card_info.present = False
                self.card_info.uid = None
                self.card_info.card_type = CARD_TYPE_UNKNOWN
                return False
                
        except Exception as e:
            logger.error(f"Card detection failed: {e}")
            self.card_info.present = False
            return False
    
    def _determine_card_type(self) -> None:
        """Determine card type based on available information"""
        # This is a simplified detection - in practice, you might need
        # to check SAK (Select Acknowledge) or ATS for accurate detection
        if self.card_info.uid:
            # For now, assume 1K by default and let authentication reveal the truth
            self.card_info.card_type = CARD_TYPE_MIFARE_1K
            self.card_info.size = 1024
            self.card_info.sectors = MIFARE_1K_SECTORS
    
    def read_block(self, block_number: int) -> Optional[bytes]:
        """Read data from specified block"""
        try:
            if not self.card_info.present:
                raise CardConnectionException("No card present")
            
            if not self._is_block_accessible(block_number):
                raise ValueError(f"Block {block_number} not accessible or not authenticated")
            
            # Prepare read command
            command = APDUCommands.READ_BINARY + [block_number, MIFARE_BLOCK_SIZE]
            
            response, sw1, sw2 = self.reader_manager.send_apdu(command)
            
            if sw1 == 0x90 and sw2 == 0x00:
                block_data = bytes(response)
                logger.debug(f"Read block {block_number}: {block_data.hex()}")
                return block_data
            else:
                logger.error(f"Read block {block_number} failed: {sw1:02X}{sw2:02X}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading block {block_number}: {e}")
            return None
    
    def write_block(self, block_number: int, data: bytes) -> bool:
        """Write data to specified block"""
        try:
            if not self.card_info.present:
                raise CardConnectionException("No card present")
            
            if len(data) != MIFARE_BLOCK_SIZE:
                raise ValueError(f"Data must be exactly {MIFARE_BLOCK_SIZE} bytes")
            
            if not self._is_block_accessible(block_number):
                raise ValueError(f"Block {block_number} not accessible or not authenticated")
            
            # Prepare write command
            command = APDUCommands.UPDATE_BINARY + [block_number, MIFARE_BLOCK_SIZE] + list(data)
            
            response, sw1, sw2 = self.reader_manager.send_apdu(command)
            
            if sw1 == 0x90 and sw2 == 0x00:
                logger.info(f"Write block {block_number} successful")
                return True
            else:
                logger.error(f"Write block {block_number} failed: {sw1:02X}{sw2:02X}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing block {block_number}: {e}")
            return False
    
    def _is_block_accessible(self, block_number: int) -> bool:
        """Check if block is accessible (authenticated)"""
        sector = self._get_sector_from_block(block_number)
        return self._authenticated_sectors.get(sector, False)
    
    def _get_sector_from_block(self, block_number: int) -> int:
        """Get sector number from block number"""
        if self.card_info.card_type == CARD_TYPE_MIFARE_1K:
            return block_number // 4
        elif self.card_info.card_type == CARD_TYPE_MIFARE_4K:
            if block_number < 32 * 4:  # First 32 sectors (4 blocks each)
                return block_number // 4
            else:  # Last 8 sectors (16 blocks each)
                return 32 + (block_number - 32 * 4) // 16
        return -1
    
    def set_sector_authenticated(self, sector: int, authenticated: bool = True) -> None:
        """Mark sector as authenticated or not"""
        self._authenticated_sectors[sector] = authenticated
        logger.debug(f"Sector {sector} authentication status: {authenticated}")
    
    def is_sector_authenticated(self, sector: int) -> bool:
        """Check if sector is authenticated"""
        return self._authenticated_sectors.get(sector, False)
    
    def get_card_info(self) -> CardInfo:
        """Get current card information"""
        return self.card_info
    
    def clear_authentication(self) -> None:
        """Clear all authentication states"""
        self._authenticated_sectors.clear()
        logger.debug("Cleared all authentication states")
