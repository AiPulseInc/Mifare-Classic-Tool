# MIFARE Classic Tool - ACR1252U Edition

## Overview

A comprehensive GUI application for MIFARE Classic card operations using the ACR1252U NFC reader. This tool provides a user-friendly interface for reading, writing, and managing MIFARE Classic 1K/4K cards with advanced security features.

## Features

### ✅ Implemented
- **Reader Management**: Auto-detection and connection to ACR1252U reader
- **Card Detection**: Automatic detection of MIFARE Classic 1K/4K cards
- **Authentication**: Support for Key A/B with default and custom keys
- **Block Operations**: Read and write individual blocks with data validation
- **Security Operations**: Key management and access condition modification
- **Safety Features**: Multiple confirmation dialogs for dangerous operations

### 🔄 Future Enhancements
- Bulk read/write operations
- Key dictionary attacks
- Data export/import functionality
- Card cloning capabilities
- Operation logging and history

## System Requirements

### Hardware
- **ACR1252U NFC Reader** (Required)
- MIFARE Classic cards (1K or 4K)
- USB port for reader connection

### Software
- Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- Python 3.8 or higher
- PC/SC service/daemon running

## Installation

### 1. Install PC/SC Drivers

**Windows:**
- Download and install ACR1252U drivers from ACS website
- PC/SC service should start automatically

**macOS:**
- PC/SC framework is built-in
- May need to install additional drivers for ACR1252U

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install pcscd pcsc-tools libpcsclite-dev
sudo systemctl start pcscd
sudo systemctl enable pcscd
```

### 2. Install Python Dependencies

```bash
# Navigate to project directory
cd NFC-tool

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\\Scripts\\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Test PC/SC installation
pcsc_scan

# Should show ACR1252U when connected
```

## Usage

### Starting the Application

```bash
python main.py
```

### Basic Workflow

1. **Connect Reader**
   - Plug in ACR1252U reader
   - Click "Connect" in Reader Status panel
   - Verify green "Connected" status

2. **Detect Card**
   - Place MIFARE Classic card on reader
   - Card information should appear automatically
   - Note the UID and card type

3. **Authenticate Sector**
   - Select target sector (0-15 for 1K, 0-39 for 4K)
   - Choose key type (A or B)
   - Enter key or use default (FF FF FF FF FF FF)
   - Click "Authenticate" or "Try Default Keys"

4. **Read Block**
   - Select block number
   - Enable "Auto-read on block change" for convenience
   - Click "Read Block" to view data
   - Data shown in hex format with optional ASCII

5. **Write Block**
   - Enter 16 bytes of data (32 hex characters)
   - Data validation ensures correct format
   - Confirm write operation (especially for trailer blocks)
   - Verify write by reading block again

### Advanced Operations

#### Key Management
⚠️ **WARNING**: Incorrect key changes can permanently lock sectors!

1. Navigate to Security Operations → Key Management tab
2. Select target sector
3. Enter new Key A, Key B, and access conditions
4. Multiple confirmation dialogs will appear
5. Sector will require re-authentication with new keys

#### Trailer Block Operations
1. Navigate to Security Operations → Trailer Blocks tab
2. Select sector and click "Read Trailer Block"
3. Keys are automatically masked for security
4. View access conditions and structure

## Project Structure

```
NFC-tool/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── config/
│   ├── constants.py          # Application constants and APDU commands
│   └── settings.py           # Settings management
├── core/
│   ├── reader_manager.py     # ACR1252U communication
│   ├── card_operations.py    # MIFARE card operations
│   ├── authentication.py     # Key management and authentication
│   └── data_utils.py         # Data conversion utilities
├── gui/
│   ├── main_window.py        # Main application window
│   ├── widgets/              # UI components
│   └── dialogs/              # Confirmation and error dialogs
├── utils/
│   ├── validators.py         # Input validation
│   ├── formatters.py         # Data formatting
│   └── logging_config.py     # Logging setup
└── tests/                    # Unit and integration tests
```

## Security Considerations

### Key Protection
- Keys are never logged or stored permanently
- Authentication keys are masked in UI displays
- Memory is cleared on application exit

### Operation Safety
- Multiple confirmation dialogs for dangerous operations
- Trailer block writes require explicit confirmation
- Input validation prevents malformed data

### Best Practices
1. **Always backup** original keys before making changes
2. **Test with expendable cards** first
3. **Understand access conditions** before modification
4. **Use default keys** only for testing/development

## Troubleshooting

### Reader Connection Issues

**Problem**: Reader not detected
- Verify USB connection
- Check PC/SC service is running
- Install/update ACR1252U drivers
- Try different USB port

### Card Detection Issues

**Problem**: Card not detected
- Ensure card is properly positioned on reader
- Try removing and replacing card
- Check if card is MIFARE Classic compatible
- Verify card is not damaged

### Authentication Issues

**Problem**: Authentication always fails
- Verify key format (12 hex characters)
- Try both Key A and Key B
- Use "Try Default Keys" function
- Card may be using custom keys

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_validators.py

# Run with coverage
python -m pytest --cov=core tests/
```

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is intended for educational and authorized testing purposes only. Users are responsible for ensuring compliance with local laws and regulations. The developers are not responsible for any misuse or damage caused by this software.

## Support

### Getting Help

1. Check this documentation
2. Review the troubleshooting section
3. Check existing issues
4. Create a new issue with:
   - Operating system and version
   - Python version
   - Complete error message
   - Steps to reproduce

---

**Happy MIFARE hacking! 🔓**
