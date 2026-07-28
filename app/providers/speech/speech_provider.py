"""
Speech-to-Text Provider Interface Module
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, List, Dict
from app.utils.logger import LoggerMixin


class SpeechToTextProvider(ABC, LoggerMixin):
    def __init__(self):
        self.logger.info(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    async def initialize(self) -> bool: pass
    @abstractmethod
    async def is_available(self) -> bool: pass
    @abstractmethod
    async def download_model(self, model_id: str, progress_callback: Optional[Callable] = None) -> bool: pass
    @abstractmethod
    async def delete_model(self, model_id: str) -> bool: pass
    @abstractmethod
    async def verify_model(self, model_id: str) -> bool: pass
    @abstractmethod
    async def transcribe(self, audio_path: str, language: Optional[str] = None, progress_callback: Optional[Callable] = None) -> Optional[str]: pass
    @abstractmethod
    async def transcribe_with_timestamps(self, audio_path: str, language: Optional[str] = None) -> List[Dict]: pass
    @abstractmethod
    async def get_available_models(self) -> List[Dict]: pass
    @abstractmethod
    async def get_model_info(self, model_id: str) -> Optional[Dict]: pass
    @abstractmethod
    async def get_disk_usage(self) -> int: pass


class SpeechProviderFactory:
    _providers = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class):
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, name: str) -> Optional[SpeechToTextProvider]:
        provider_class = cls._providers.get(name)
        if provider_class:
            try:
                return provider_class()
            except Exception as e:
                SpeechToTextProvider.logger.error(f"Failed to create provider {name}: {e}")
                return None
        return None
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        return list(cls._providers.keys())
