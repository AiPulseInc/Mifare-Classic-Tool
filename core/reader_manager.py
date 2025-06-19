"""
ACR1252U Reader Manager
Handles PC/SC communication and reader operations
"""

import logging
import threading
import time
from typing import List, Optional, Tuple, Callable
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
from smartcard.CardConnection import CardConnection
from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType
from smartcard.Exceptions import NoCardException, CardConnectionException
from smartcard.pcsc.PCSCExceptions import EstablishContextException

from config.constants import ACR1252U_READER_NAME, ESCAPE_COMMAND, APDUCommands, ErrorCodes

logger = logging.getLogger(__name__)

class ReaderStatus:
    """Reader status enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class ReaderManager:
    """Manages ACR1252U reader connection and basic operations"""
    
    def __init__(self):
        self.reader = None
        self.connection = None
        self.status = ReaderStatus.DISCONNECTED
        self.firmware_version = None
        self.status_callbacks: List[Callable] = []
        self._monitoring = False
        self._monitor_thread = None
    
    def add_status_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback for status changes"""
        self.status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: Callable[[str], None]) -> None:
        """Remove status callback"""
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)
    
    def _notify_status_change(self, status: str) -> None:
        """Notify all callbacks about status change"""
        self.status = status
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def get_available_readers(self) -> List[str]:
        """Get list of available PC/SC readers"""
        try:
            reader_list = readers()
            return [str(reader) for reader in reader_list]
        except EstablishContextException as e:
            logger.error(f"Failed to establish PC/SC context: {e}")
            return []
    
    def find_acr1252u_reader(self) -> Optional[str]:
        """Find ACR1252U reader in available readers"""
        available_readers = self.get_available_readers()
        
        for reader_name in available_readers:
            if ACR1252U_READER_NAME in reader_name or "ACR1252" in reader_name:
                logger.info(f"Found ACR1252U reader: {reader_name}")
                return reader_name
        
        logger.warning("ACR1252U reader not found")
        return None
    
    def connect(self, reader_name: Optional[str] = None) -> bool:
        """Connect to ACR1252U reader"""
        try:
            self._notify_status_change(ReaderStatus.CONNECTING)
            
            # Find reader if not specified
            if reader_name is None:
                reader_name = self.find_acr1252u_reader()
                if reader_name is None:
                    self._notify_status_change(ReaderStatus.ERROR)
                    return False
            
            # Get reader object
            reader_list = readers()
            self.reader = None
            
            for r in reader_list:
                if reader_name in str(r):
                    self.reader = r
                    break
            
            if self.reader is None:
                logger.error(f"Reader {reader_name} not found in available readers")
                self._notify_status_change(ReaderStatus.ERROR)
                return False
            
            # Establish connection to the reader
            self.connection = self.reader.createConnection()
            self.connection.connect()

            # Update status so that subsequent commands succeed
            self._notify_status_change(ReaderStatus.CONNECTED)

            logger.info(f"Connected to reader: {self.reader}")

            # Get firmware version now that the connection is active
            self._get_firmware_version()

            # Start monitoring thread
            self._start_monitoring()

            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to reader: {e}")
            self._notify_status_change(ReaderStatus.ERROR)
            return False
    
    def disconnect(self) -> None:
        """Disconnect from reader"""
        try:
            # Stop monitoring
            self._stop_monitoring()
            
            # Disconnect card connection
            if self.connection:
                self.connection.disconnect()
                self.connection = None
            
            self.reader = None
            self.firmware_version = None
            
            logger.info("Disconnected from reader")
            self._notify_status_change(ReaderStatus.DISCONNECTED)
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            self._notify_status_change(ReaderStatus.ERROR)
    
    def is_connected(self) -> bool:
        """Check if reader is connected"""
        return self.status == ReaderStatus.CONNECTED and self.connection is not None
    
    def send_escape_command(self, command: List[int]) -> Tuple[List[int], int, int]:
        """Send escape command to reader"""
        if not self.is_connected():
            raise CardConnectionException("Reader not connected")
        
        try:
            response, sw1, sw2 = self.connection.control(ESCAPE_COMMAND, command)
            logger.debug(f"Escape command: {toHexString(command)} -> {toHexString(response)} {sw1:02X}{sw2:02X}")
            return response, sw1, sw2
        except Exception as e:
            logger.error(f"Escape command failed: {e}")
            raise
    
    def send_apdu(self, command: List[int]) -> Tuple[List[int], int, int]:
        """Send APDU command to card"""
        if not self.is_connected():
            raise CardConnectionException("Reader not connected")
        
        try:
            response, sw1, sw2 = self.connection.transmit(command)
            logger.debug(f"APDU: {toHexString(command)} -> {toHexString(response)} {sw1:02X}{sw2:02X}")
            return response, sw1, sw2
        except Exception as e:
            logger.error(f"APDU command failed: {e}")
            raise
    
    def _get_firmware_version(self) -> None:
        """Get reader firmware version"""
        try:
            response, sw1, sw2 = self.send_escape_command(APDUCommands.GET_FIRMWARE_VERSION)
            
            if sw1 == 0xE1 and len(response) > 5:
                # Extract firmware version string
                version_length = response[4]
                version_bytes = response[5:5+version_length]
                self.firmware_version = ''.join(chr(b) for b in version_bytes)
                logger.info(f"Firmware version: {self.firmware_version}")
            else:
                logger.warning("Failed to get firmware version")
                
        except Exception as e:
            logger.error(f"Error getting firmware version: {e}")
    
    def _start_monitoring(self) -> None:
        """Start reader monitoring thread"""
        if not self._monitoring:
            self._monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor_reader, daemon=True)
            self._monitor_thread.start()
            logger.debug("Started reader monitoring")
    
    def _stop_monitoring(self) -> None:
        """Stop reader monitoring thread"""
        self._monitoring = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
            logger.debug("Stopped reader monitoring")
    
    def _monitor_reader(self) -> None:
        """Monitor reader connection in background thread"""
        while self._monitoring:
            try:
                if self.connection:
                    # Try to send a simple command to check connection
                    self.send_escape_command(APDUCommands.GET_FIRMWARE_VERSION)
                time.sleep(2.0)  # Check every 2 seconds
            except Exception as e:
                logger.warning(f"Reader monitoring detected disconnection: {e}")
                self._notify_status_change(ReaderStatus.ERROR)
                break
    
    def get_reader_info(self) -> dict:
        """Get reader information"""
        return {
            "name": str(self.reader) if self.reader else None,
            "status": self.status,
            "firmware_version": self.firmware_version,
            "connected": self.is_connected()
        }
