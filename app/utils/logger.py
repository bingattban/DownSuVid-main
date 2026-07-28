"""
Logging Utility Module
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler
from kivy.utils import platform

from app.config.constants import STORAGE_ROOT, STORAGE_LOGS, MAX_LOG_SIZE


class ArabicFormatter(logging.Formatter):
    """Custom formatter with Arabic support"""
    
    def format(self, record):
        record.asctime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return super().format(record)


def _get_log_dir() -> Path:
    """Get platform-safe logs directory"""
    if platform == 'android':
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, 'user_data_dir'):
            return Path(app.user_data_dir) / STORAGE_LOGS
        return Path(f"/data/data/com.downsuviid/files") / STORAGE_LOGS
    return Path.home() / f".{STORAGE_ROOT.lower()}" / STORAGE_LOGS


def setup_logger(name: str = 'DownSuVid', level: int = logging.INFO) -> logging.Logger:
    """Setup application logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    logger.handlers.clear()
    
    console_formatter = ArabicFormatter('[%(asctime)s] [%(levelname)s] %(message)s')
    file_formatter = ArabicFormatter('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s')
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    try:
        log_dir = _get_log_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
    except Exception as e:
        logger.warning(f"Failed to setup file logging: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger for a module"""
    return logging.getLogger(f'DownSuVid.{name}')


class LoggerMixin:
    """Mixin class for adding logging capabilities"""
    
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
