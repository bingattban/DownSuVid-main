"""
Database Manager Module
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Tuple, Any
from contextlib import contextmanager
from kivy.utils import platform
from kivy.app import App
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.config.constants import (
    STORAGE_ROOT,
    STORAGE_DATABASE,
    DATABASE_NAME,
    DATABASE_VERSION
)


class DatabaseManager(LoggerMixin):
    """Database Manager for SQLite operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self._connection: Optional[sqlite3.Connection] = None
        self._db_path: Optional[Path] = None
        self.logger.info("DatabaseManager created")
    
    def _get_db_dir(self) -> Path:
        """Get platform-safe database directory"""
        if platform == 'android':
            app = App.get_running_app()
            if app and hasattr(app, 'user_data_dir'):
                return Path(app.user_data_dir) / STORAGE_DATABASE
            return Path(f"/data/data/com.downsuviid/files") / STORAGE_DATABASE
        return Path.home() / f".{STORAGE_ROOT.lower()}" / STORAGE_DATABASE

    def initialize(self, db_path: Optional[str] = None) -> None:
        """Initialize database"""
        try:
            if db_path is None:
                db_dir = self._get_db_dir()
                db_dir.mkdir(parents=True, exist_ok=True)
                self._db_path = db_dir / DATABASE_NAME
            else:
                self._db_path = Path(db_path)
            
            self._create_connection()
            self._run_migrations()
            self.logger.info(f"Database initialized at {self._db_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_connection(self) -> None:
        try:
            self._connection = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
                timeout=10
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._connection.execute("PRAGMA encoding='UTF-8'")
        except Exception as e:
            self.logger.error(f"Failed to create connection: {e}")
            raise
    
    def _run_migrations(self) -> None:
        try:
            from app.database.migrations.migration_manager import MigrationManager
            migration_manager = MigrationManager(self)
            migration_manager.run_migrations()
        except ImportError:
            self.logger.warning("MigrationManager not found, skipping migrations")
    
    @contextmanager
    def get_cursor(self):
        if not self._connection:
            self.initialize()
            
        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def execute(self, query: str, params: Optional[Tuple] = None) -> None:
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[sqlite3.Row]:
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[sqlite3.Row]:
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def get_count(self, table: str, where: Optional[str] = None, params: Optional[Tuple] = None) -> int:
        query = f"SELECT COUNT(*) as count FROM {table}"
        if where:
            query += f" WHERE {where}"
        
        result = self.fetch_one(query, params)
        return result['count'] if result else 0
    
    def table_exists(self, table: str) -> bool:
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetch_one(query, (table,))
        return result is not None
    
    def get_database_size(self) -> int:
        if self._db_path and self._db_path.exists():
            return self._db_path.stat().st_size
        return 0
    
    def vacuum(self) -> None:
        self.execute("VACUUM")
        self.logger.info("Database vacuumed")
    
    def backup(self, backup_path: Optional[str] = None) -> bool:
        try:
            if backup_path is None:
                backup_dir = self._get_db_dir() / 'backups'
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            source = sqlite3.connect(str(self._db_path))
            dest = sqlite3.connect(str(backup_path))
            source.backup(dest)
            dest.close()
            source.close()
            
            self.logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False
    
    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
            self.logger.info("Database connection closed")
