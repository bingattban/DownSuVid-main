"""
Translation Provider Interface Module
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, List, Dict
from app.utils.logger import LoggerMixin


class TranslationProvider(ABC, LoggerMixin):
    def __init__(self):
        self.logger.info(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    async def initialize(self) -> bool: pass
    @abstractmethod
    async def is_available(self) -> bool: pass
    @abstractmethod
    async def download_package(self, source_lang: str, target_lang: str, progress_callback: Optional[Callable] = None) -> bool: pass
    @abstractmethod
    async def delete_package(self, source_lang: str, target_lang: str) -> bool: pass
    @abstractmethod
    async def verify_package(self, source_lang: str, target_lang: str) -> bool: pass
    @abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str = "ar") -> Optional[str]: pass
    @abstractmethod
    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str = "ar") -> List[Optional[str]]: pass
    @abstractmethod
    async def detect_language(self, text: str) -> Optional[str]: pass
    @abstractmethod
    async def get_available_packages(self) -> List[Dict]: pass
    @abstractmethod
    async def get_installed_packages(self) -> List[Dict]: pass
    @abstractmethod
    async def is_package_installed(self, source_lang: str, target_lang: str) -> bool: pass
    @abstractmethod
    async def get_disk_usage(self) -> int: pass

class TranslationProviderFactory:
    _providers = {}
    @classmethod
    def register_provider(cls, name: str, provider_class): cls._providers[name] = provider_class
    @classmethod
    def create_provider(cls, name: str) -> Optional[TranslationProvider]:
        provider_class = cls._providers.get(name)
        if provider_class:
            try: return provider_class()
            except Exception as e:
                TranslationProvider.logger.error(f"Failed to create provider {name}: {e}")
                return None
        return None
    @classmethod
    def get_available_providers(cls) -> List[str]: return list(cls._providers.keys())
