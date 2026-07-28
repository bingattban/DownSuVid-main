"""
Application Configuration Manager
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Optional, Dict
from kivy.utils import platform
from kivy.app import App

from app.utils.logger import get_logger

logger = get_logger(__name__)


class AppConfig:
    """Application Configuration Manager"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        self._defaults: Dict[str, Any] = {
            'language': 'ar',
            'theme': 'dark',
            'video_quality': '720p',
            'subtitle_format': 'srt',
            'download_folder': 'Downloads',
            'max_parallel_downloads': 3,
            'auto_resume': True,
            'auto_clean_cache': False,
            'auto_check_updates': True,
            'speech_engine': 'whisper',
            'translation_engine': 'argos',
            'notification_enabled': True,
            'analytics_enabled': False,
        }
    
    def _get_config_dir(self) -> Path:
        """Get platform-specific configuration directory"""
        from app.config.constants import STORAGE_CONFIG, STORAGE_ROOT
        
        if platform == 'android':
            app = App.get_running_app()
            if app and hasattr(app, 'user_data_dir'):
                base = Path(app.user_data_dir)
            else:
                base = Path(f"/data/data/com.downsuviid/files")
        else:
            base = Path.home() / f".{STORAGE_ROOT.lower()}"
            
        return base / STORAGE_CONFIG

    def load_config(self, config_path: Optional[str] = None) -> None:
        """Load configuration from file"""
        try:
            if config_path is None:
                base_path = self._get_config_dir()
                base_path.mkdir(parents=True, exist_ok=True)
                self._config_path = base_path / 'config.json'
            else:
                self._config_path = Path(config_path)
            
            if self._config_path.exists():
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info(f"Configuration loaded from {self._config_path}")
            else:
                logger.info("No configuration file found, using defaults")
                self._config = self._defaults.copy()
                self.save_config()
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._config = self._defaults.copy()
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            if self._config_path is None:
                return False
            
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            
            logger.debug("Configuration saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, self._defaults.get(key, default))
    
    def set(self, key: str, value: Any) -> bool:
        try:
            self._config[key] = value
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"Failed to set configuration: {e}")
            return False
    
    def reset(self, key: Optional[str] = None) -> bool:
        try:
            if key is None:
                self._config = self._defaults.copy()
            else:
                if key in self._defaults:
                    self._config[key] = self._defaults[key]
                else:
                    self._config.pop(key, None)
            
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        return self._config.copy()
