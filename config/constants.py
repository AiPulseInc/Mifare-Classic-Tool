"""
MIFARE Classic Tool Constants
Contains all APDU commands, card constants, and application settings
"""

# MIFARE Classic Card Constants
MIFARE_CLASSIC_1K_SIZE = 1024
MIFARE_CLASSIC_4K_SIZE = 4096
MIFARE_BLOCK_SIZE = 16
MIFARE_SECTOR_SIZE = 4  # blocks per sector (except last sectors in 4K)

# Card Types
CARD_TYPE_UNKNOWN = 0
CARD_TYPE_MIFARE_1K = 1
CARD_TYPE_MIFARE_4K = 2

CARD_TYPE_NAMES = {
    CARD_TYPE_UNKNOWN: "Unknown",
    CARD_TYPE_MIFARE_1K: "MIFARE Classic 1K",
    CARD_TYPE_MIFARE_4K: "MIFARE Classic 4K"
}

# MIFARE Classic Memory Structure
MIFARE_1K_SECTORS = 16
MIFARE_4K_SECTORS = 40

# Key Types
KEY_TYPE_A = 0x60
KEY_TYPE_B = 0x61

KEY_TYPE_NAMES = {
    KEY_TYPE_A: "Key A",
    KEY_TYPE_B: "Key B"
}

# Default Keys
DEFAULT_KEY = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
TRANSPORT_KEY = bytes([0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5])

# ACR1252U Specific Constants
ACR1252U_READER_NAME = "ACS ACR1252 1S CL Reader PICC"
ESCAPE_COMMAND = 0x310000 + 3500 * 4

# APDU Commands (based on API documentation)
class APDUCommands:
    """APDU commands for ACR1252U and MIFARE operations"""
    
    # Peripheral Control Commands
    GET_FIRMWARE_VERSION = [0xE0, 0x00, 0x00, 0x18, 0x00]
    LED_CONTROL = [0xE0, 0x00, 0x00, 0x29, 0x01]
    BUZZER_CONTROL = [0xE0, 0x00, 0x00, 0x28, 0x01]
    
    # PICC Commands
    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    GET_ATS = [0xFF, 0xCA, 0x01, 0x00, 0x00]
    
    # Authentication Commands
    LOAD_AUTH_KEY = [0xFF, 0x82, 0x00, 0x00, 0x06]
    AUTH_BLOCK = [0xFF, 0x86, 0x00, 0x00, 0x05]
    
    # Read/Write Commands
    READ_BINARY = [0xFF, 0xB0, 0x00]  # + block_number + length
    UPDATE_BINARY = [0xFF, 0xD6, 0x00]  # + block_number + length + data

# LED Control Values
LED_OFF = 0x00
LED_RED_ON = 0x01
LED_GREEN_ON = 0x02
LED_BOTH_ON = 0x03

# Error Codes
class ErrorCodes:
    """Standard error codes for the application"""
    SUCCESS = 0x9000
    AUTHENTICATION_FAILED = 0x6300
    OPERATION_FAILED = 0x6300
    CARD_NOT_FOUND = 0x6200
    INVALID_BLOCK = 0x6A00

# Application Settings
class AppSettings:
    """Application-wide settings"""
    
    # UI Settings
    WINDOW_TITLE = "MIFARE Classic Tool - ACR1252U Edition"
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    
    # Operation Timeouts (milliseconds)
    READER_CONNECT_TIMEOUT = 5000
    CARD_OPERATION_TIMEOUT = 3000
    
    # Validation Settings
    MAX_KEY_INPUT_LENGTH = 12  # for hex input (6 bytes = 12 hex chars)
    MAX_BLOCK_DATA_LENGTH = 32  # for hex input (16 bytes = 32 hex chars)
    
    # Logging Settings
    LOG_FILE_NAME = "mifare_tool.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
