"""
Translation Service Module
"""

import asyncio
from typing import Optional, List, Dict
from pathlib import Path

from app.utils.logger import LoggerMixin
from app.utils.file_utils import FileUtils
from app.domain.entities.subtitle import Subtitle, SubtitleFormat
from app.providers.translation.translation_provider import (
    TranslationProvider,
    TranslationProviderFactory
)
from app.config.app_config import AppConfig


class TranslationService(LoggerMixin):
    """Service for translation operations"""
    
    def __init__(self):
        self.config = AppConfig()
        self.provider: Optional[TranslationProvider] = None
        self._initialized = False
        self.logger.info("TranslationService initialized")
    
    async def initialize(self) -> bool:
        if self._initialized: return True
        try:
            provider_name = self.config.get('translation_engine', 'argos')
            self.provider = TranslationProviderFactory.create_provider(provider_name)
            
            if self.provider:
                self._initialized = await self.provider.initialize()
                if self._initialized:
                    self.logger.info(f"Translation provider ready: {provider_name}")
                else:
                    self.logger.warning(f"Translation provider not available: {provider_name}")
            else:
                self.logger.warning(f"No translation provider found: {provider_name}")
                self._initialized = False
            return self._initialized
        except Exception as e:
            self.logger.error(f"Failed to initialize translation: {e}")
            self._initialized = False
            return False
    
    async def is_available(self) -> bool:
        if not self._initialized: await self.initialize()
        return await self.provider.is_available() if self.provider else False
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str = "ar") -> Optional[str]:
        try:
            if not await self.is_available(): return None
            return await self.provider.translate(text, source_lang, target_lang)
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            return None
    
    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str = "ar") -> List[Optional[str]]:
        try:
            if not await self.is_available(): return [None] * len(texts)
            return await self.provider.translate_batch(texts, source_lang, target_lang)
        except Exception as e:
            self.logger.error(f"Batch translation failed: {e}")
            return [None] * len(texts)
    
    async def translate_subtitle(self, subtitle: Subtitle, target_lang: str = "ar") -> Optional[Subtitle]:
        try:
            if not subtitle.content: return None
            
            entries = subtitle.parse_content()
            if not entries: return None
            
            texts = [entry['text'] for entry in entries]
            source_lang = subtitle.language
            if not source_lang and self.provider:
                source_lang = await self.provider.detect_language(' '.join(texts)) or 'en'
            
            translated_texts = await self.translate_batch(texts, source_lang, target_lang)
            
            translated_entries = []
            for entry, translated_text in zip(entries, translated_texts):
                if translated_text:
                    entry['text'] = translated_text
                    translated_entries.append(entry)
            
            if not translated_entries: return None
            
            srt_content = self._build_srt(translated_entries)
            output_path = FileUtils.get_subtitle_path()
            original_name = Path(subtitle.file_path).stem if subtitle.file_path else "subtitle"
            translated_file = str(output_path / f"{original_name}_ar.srt")
            
            with open(translated_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            return Subtitle(
                language=target_lang, language_name='العربية', format=SubtitleFormat.SRT,
                source=subtitle.source, priority=subtitle.priority, file_path=translated_file,
                content=srt_content, original_content=subtitle.content,
                original_language=source_lang, translated_from=source_lang,
                translation_engine=self.config.get('translation_engine'),
            )
        except Exception as e:
            self.logger.error(f"Subtitle translation failed: {e}")
            return None
    
    def _build_srt(self, entries: List[Dict]) -> str:
        srt_lines = []
        for i, entry in enumerate(entries, 1):
            start = self._seconds_to_srt_time(entry['start_time'])
            end = self._seconds_to_srt_time(entry['end_time'])
            srt_lines.extend([str(i), f"{start} --> {end}", entry['text'], ""])
        return '\n'.join(srt_lines)
    
    @staticmethod
    def _seconds_to_srt_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millis = int((secs - int(secs)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millis:03d}"
    
    async def detect_language(self, text: str) -> Optional[str]:
        if not await self.is_available(): return None
        return await self.provider.detect_language(text)
    
    async def get_available_packages(self) -> List[Dict]:
        if not self._initialized: await self.initialize()
        return await self.provider.get_available_packages() if self.provider else []
    
    async def get_installed_packages(self) -> List[Dict]:
        if not self._initialized: await self.initialize()
        return await self.provider.get_installed_packages() if self.provider else []
    
    async def download_package(self, source_lang: str, target_lang: str) -> bool:
        if not self._initialized: await self.initialize()
        return await self.provider.download_package(source_lang, target_lang) if self.provider else False
    
    async def delete_package(self, source_lang: str, target_lang: str) -> bool:
        if not self._initialized: await self.initialize()
        return await self.provider.delete_package(source_lang, target_lang) if self.provider else False
