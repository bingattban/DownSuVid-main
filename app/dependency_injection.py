"""
Dependency Injection Container
Centralized dependency management for the application
"""

from typing import Dict, Any, Optional
from app.utils.logger import LoggerMixin


class DIContainer(LoggerMixin):
    """Simple Dependency Injection Container"""
    
    _instance = None
    _services: Dict[str, Any] = {}
    _repositories: Dict[str, Any] = {}
    _providers: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DIContainer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized: return
        self._initialized = True
        self.logger.info("DI Container initialized")
    
    def register_service(self, name: str, service: Any):
        self._services[name] = service
        self.logger.debug(f"Service registered: {name}")
    
    def register_repository(self, name: str, repository: Any):
        self._repositories[name] = repository
        self.logger.debug(f"Repository registered: {name}")
    
    def register_provider(self, name: str, provider: Any):
        self._providers[name] = provider
        self.logger.debug(f"Provider registered: {name}")
    
    def get_service(self, name: str) -> Optional[Any]: return self._services.get(name)
    def get_repository(self, name: str) -> Optional[Any]: return self._repositories.get(name)
    def get_provider(self, name: str) -> Optional[Any]: return self._providers.get(name)
    
    def initialize_all(self):
        """Initialize all core services safely"""
        try:
            from app.database.database_manager import DatabaseManager
            db = DatabaseManager()
            db.initialize()
            self.register_service('database', db)
            
            from app.config.app_config import AppConfig
            config = AppConfig()
            config.load_config()
            self.register_service('config', config)
            
            from app.services.storage.storage_service import StorageService
            storage = StorageService()
            self.register_service('storage', storage)
            
            from app.services.download.download_service import DownloadService
            download_service = DownloadService()
            self.register_service('download', download_service)
            
            from app.services.subtitle.subtitle_service import SubtitleService
            subtitle_service = SubtitleService()
            self.register_service('subtitle', subtitle_service)
            
            from app.services.settings.settings_service import SettingsService
            settings_service = SettingsService()
            self.register_service('settings', settings_service)

            # حقن مرن للخدمات غير الأساسية التي قد لا تكون موجودة (لتجنب الانهيار)
            try:
                from app.services.queue.queue_service import QueueService
                self.register_service('queue', QueueService())
            except ImportError: pass

            try:
                from app.services.models.model_service import ModelService
                self.register_service('model', ModelService())
            except ImportError: pass
            
            try:
                from app.services.packages.package_service import PackageService
                self.register_service('package', PackageService())
            except ImportError: pass
            
            try:
                from app.services.history.history_service import HistoryService
                self.register_service('history', HistoryService())
            except ImportError: pass
            
            # Repositories (حقن مرن)
            try:
                from app.repositories.download_repository_impl import DownloadRepositoryImpl
                self.register_repository('download', DownloadRepositoryImpl())
                
                from app.repositories.settings_repository_impl import SettingsRepositoryImpl
                self.register_repository('settings', SettingsRepositoryImpl())
                
                from app.repositories.model_repository_impl import ModelRepositoryImpl
                self.register_repository('model', ModelRepositoryImpl())
                
                from app.repositories.package_repository_impl import PackageRepositoryImpl
                self.register_repository('package', PackageRepositoryImpl())
                
                from app.repositories.subtitle_repository_impl import SubtitleRepositoryImpl
                self.register_repository('subtitle', SubtitleRepositoryImpl())
            except ImportError: pass
            
            self.logger.info("All dependencies initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dependencies: {e}")
    
    def shutdown(self):
        try:
            if 'database' in self._services: self._services['database'].close()
            self._services.clear()
            self._repositories.clear()
            self._providers.clear()
            self.logger.info("All services shutdown")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

# Global DI instance
di_container = DIContainer()
