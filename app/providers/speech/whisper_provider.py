"""
Whisper Provider Implementation
"""

import os
from typing import Optional, Callable, List, Dict
from app.utils.logger import LoggerMixin
from app.providers.speech.speech_provider import SpeechToTextProvider
from app.utils.file_utils import FileUtils


class WhisperProvider(SpeechToTextProvider):
    """Whisper speech-to-text provider"""
    
    def __init__(self):
        super().__init__()
        self._model = None
        self._model_id = None
        self._model_dir = str(FileUtils.get_model_path('whisper'))
        self.logger.info("WhisperProvider created")
    
    async def initialize(self) -> bool:
        try:
            import whisper
            self._whisper_module = whisper
            FileUtils.ensure_directory(self._model_dir)
            self.logger.info("Whisper initialized")
            return True
        except ImportError:
            self.logger.warning("Whisper not installed - Will be disabled on Android")
            return False
        except Exception as e:
            self.logger.error(f"Whisper initialization failed: {e}")
            return False
    
    async def is_available(self) -> bool:
        try:
            import whisper
            return True
        except ImportError:
            return False
    
    async def download_model(self, model_id: str, progress_callback: Optional[Callable] = None) -> bool:
        try:
            import whisper
            self.logger.info(f"Downloading Whisper model: {model_id}")
            self._model = whisper.load_model(model_id, download_root=self._model_dir)
            self._model_id = model_id
            
            if progress_callback:
                await progress_callback(model_id, 100.0, 'completed')
            return True
        except Exception as e:
            self.logger.error(f"Failed to download model: {e}")
            return False
    
    async def delete_model(self, model_id: str) -> bool:
        try:
            if os.path.exists(self._model_dir):
                model_file = os.path.join(self._model_dir, f"{model_id}.pt")
                if os.path.exists(model_file):
                    os.remove(model_file)
                    self.logger.info(f"Model deleted: {model_id}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete model: {e}")
            return False
    
    async def verify_model(self, model_id: str) -> bool:
        model_file = os.path.join(self._model_dir, f"{model_id}.pt")
        return os.path.exists(model_file)
    
    async def transcribe(self, audio_path: str, language: Optional[str] = None, progress_callback: Optional[Callable] = None) -> Optional[str]:
        try:
            if not self._model: return None
            options = {'language': language} if language else {}
            result = self._model.transcribe(audio_path, **options)
            return result.get('text', '')
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return None
    
    async def transcribe_with_timestamps(self, audio_path: str, language: Optional[str] = None) -> List[Dict]:
        try:
            if not self._model: return []
            options = {'language': language} if language else {}
            result = self._model.transcribe(audio_path, **options)
            
            segments = []
            for seg in result.get('segments', []):
                segments.append({
                    'text': seg.get('text', '').strip(),
                    'start': seg.get('start', 0),
                    'end': seg.get('end', 0),
                    'confidence': seg.get('confidence', 0),
                })
            return segments
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return []
    
    async def get_available_models(self) -> List[Dict]:
        return [
            {'id': 'tiny', 'name': 'Whisper Tiny', 'size': 75 * 1024 * 1024, 'language': 'multi', 'description': 'أسرع نموذج - دقة أقل'},
            {'id': 'base', 'name': 'Whisper Base', 'size': 145 * 1024 * 1024, 'language': 'multi', 'description': 'توازن بين السرعة والدقة'},
            {'id': 'small', 'name': 'Whisper Small', 'size': 488 * 1024 * 1024, 'language': 'multi', 'description': 'دقة جيدة'},
        ]
    
    async def get_model_info(self, model_id: str) -> Optional[Dict]:
        models = await self.get_available_models()
        for model in models:
            if model['id'] == model_id: return model
        return None
    
    async def get_disk_usage(self) -> int:
        try:
            if os.path.exists(self._model_dir):
                return sum(os.path.getsize(os.path.join(self._model_dir, f)) for f in os.listdir(self._model_dir) if os.path.isfile(os.path.join(self._model_dir, f)))
            return 0
        except Exception:
            return 0
