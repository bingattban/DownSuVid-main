"""
Speech Service Module
"""

import os
import asyncio
from typing import Optional, List, Dict
from pathlib import Path

from app.utils.logger import LoggerMixin
from app.providers.speech.speech_provider import SpeechProviderFactory
from app.config.app_config import AppConfig


class SpeechService(LoggerMixin):
    def __init__(self):
        self.config = AppConfig()
        self.provider = None
        self._initialized = False
        self.logger.info("SpeechService initialized")
    
    async def initialize(self) -> bool:
        if self._initialized: return True
        try:
            provider_name = self.config.get('speech_engine', 'whisper')
            self.provider = SpeechProviderFactory.create_provider(provider_name)
            
            if self.provider:
                self._initialized = await self.provider.initialize()
                if self._initialized:
                    self.logger.info(f"Speech provider ready: {provider_name}")
                else:
                    self.logger.warning(f"Speech provider not available: {provider_name}")
            else:
                self.logger.warning(f"No speech provider found: {provider_name}")
                self._initialized = False
            return self._initialized
        except Exception as e:
            self.logger.error(f"Failed to initialize speech: {e}")
            self._initialized = False
            return False
    
    async def is_available(self) -> bool:
        if not self._initialized: await self.initialize()
        return await self.provider.is_available() if self.provider else False
    
    async def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Optional[Dict]:
        try:
            if not await self.is_available() or not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                return None
            
            segments = await self.provider.transcribe_with_timestamps(audio_path, language)
            if not segments:
                text = await self.provider.transcribe(audio_path, language)
                if text: segments = [{'text': text, 'start': 0, 'end': 0}]
                else: return None
            
            confidence = sum(s.get('confidence', 0) for s in segments) / len(segments) if segments else 0
            detected_lang = language or await self._detect_language_simple(' '.join(s.get('text', '') for s in segments))
            
            return {
                'text': ' '.join(s.get('text', '') for s in segments), 'segments': segments,
                'language': detected_lang or 'en', 'confidence': confidence, 'duration': segments[-1].get('end', 0) if segments else 0,
            }
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return None
    
    async def _detect_language_simple(self, text: str) -> Optional[str]:
        if not text: return None
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06ff')
        return 'ar' if arabic_chars > len(text) * 0.3 else 'en'
    
    async def get_available_models(self) -> List[Dict]: return await self.provider.get_available_models() if self.provider else []
    async def download_model(self, model_id: str) -> bool: return await self.provider.download_model(model_id) if self.provider else False
    async def delete_model(self, model_id: str) -> bool: return await self.provider.delete_model(model_id) if self.provider else False
    async def verify_model(self, model_id: str) -> bool: return await self.provider.verify_model(model_id) if self.provider else False
    async def get_model_info(self, model_id: str) -> Optional[Dict]: return await self.provider.get_model_info(model_id) if self.provider else None
    async def get_disk_usage(self) -> int: return await self.provider.get_disk_usage() if self.provider else 0
