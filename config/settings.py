"""
Application settings management
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class Settings:
    """Application settings manager"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".mifare_classic_tool"
        self.config_file = self.config_dir / "settings.json"
        self._settings = self._load_default_settings()
        self._load_settings()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings"""
        return {
            "reader": {
                "auto_connect": True,
                "connection_timeout": 5000
            },
            "ui": {
                "theme": "default",
                "remember_window_size": True,
                "window_geometry": None
            },
            "operations": {
                "confirm_write_operations": True,
                "confirm_key_changes": True,
                "auto_authenticate_on_read": True
            },
            "logging": {
                "level": "INFO",
                "enable_file_logging": True,
                "max_log_size": 10485760  # 10MB
            }
        }
    
    def _load_settings(self) -> None:
        """Load settings from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                    self._settings.update(saved_settings)
        except Exception as e:
            print(f"Warning: Could not load settings: {e}")
    
    def save_settings(self) -> None:
        """Save current settings to file"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get setting value using dot notation (e.g., 'reader.auto_connect')"""
        keys = key_path.split('.')
        value = self._settings
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """Set setting value using dot notation"""
        keys = key_path.split('.')
        settings = self._settings
        
        for key in keys[:-1]:
            if key not in settings:
                settings[key] = {}
            settings = settings[key]
        
        settings[keys[-1]] = value
        self.save_settings()

# Global settings instance
settings = Settings()
