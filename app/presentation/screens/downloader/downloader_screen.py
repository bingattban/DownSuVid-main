"""
Downloader Screen Module
"""

import asyncio
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from kivy.utils import platform

from app.utils.logger import LoggerMixin
from app.services.download.download_service import DownloadService
from app.services.subtitle.subtitle_service import SubtitleService

class DownloaderScreen(MDScreen, LoggerMixin):
    """Downloader screen for URL input and video info"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.download_service = DownloadService()
        self.subtitle_service = SubtitleService()
        self.current_download_id = None
        self.video_info = None
    
    def paste_url(self):
        try:
            from kivy.core.clipboard import Clipboard
            clipboard_text = Clipboard.paste()
            if clipboard_text:
                self.ids.url_input.text = clipboard_text
        except Exception as e:
            self.logger.error(f"Failed to paste URL: {e}")
            self.show_error("فشل في لصق الرابط")
    
    def clear_url(self):
        self.ids.url_input.text = ""
    
    def clear_all(self):
        self.clear_url()
        self.video_info = None
        self.current_download_id = None
    
    def analyze_url(self):
        url = self.ids.url_input.text.strip()
        if not url: return self.show_error("الرجاء إدخال رابط الفيديو")
        self.ids.analyze_btn.disabled = True
        self.ids.analyze_btn.text = "جاري التحليل..."
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self._analyze_url_async(url)))
    
    async def _analyze_url_async(self, url: str):
        try:
            self.video_info = await self.download_service.analyze_url(url)
            if not self.video_info:
                Clock.schedule_once(lambda dt: self.show_error("فشل في تحليل الرابط"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"خطأ: {str(e)}"))
        finally:
            Clock.schedule_once(lambda dt: self._reset_analyze_button())

    def _reset_analyze_button(self):
        self.ids.analyze_btn.disabled = False
        self.ids.analyze_btn.text = "تحليل الرابط"
    
    def show_error(self, message: str):
        dialog = MDDialog(
            title="خطأ", text=message,
            buttons=[MDFlatButton(text="موافق", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
        
    def show_history(self):
        self.manager.current = 'downloads'
