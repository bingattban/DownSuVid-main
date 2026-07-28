"""
Downloads Screen Module
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.progressbar import MDProgressBar
from kivy.clock import Clock
import asyncio

from app.utils.logger import LoggerMixin
from app.services.download.download_service import DownloadService

class DownloadsScreen(MDScreen, LoggerMixin):
    """Screen for managing downloads"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.download_service = DownloadService()
    
    def on_enter(self):
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self._refresh_downloads()))
    
    async def _refresh_downloads(self):
        try:
            downloads = await self.download_service.get_downloads()
            Clock.schedule_once(lambda dt: self._update_downloads_list(downloads))
        except Exception as e:
            self.logger.error(f"Failed to refresh downloads: {e}")
    
    def _update_downloads_list(self, downloads):
        self.ids.downloads_list.clear_widgets()
        if not downloads:
            empty_label = MDLabel(
                text='لا توجد تحميلات حالياً', halign='center', font_style='Subtitle1',
                theme_text_color='Secondary', opacity=0.5, size_hint_y=None, height=100
            )
            self.ids.downloads_list.add_widget(empty_label)
            return
    
    def clear_completed(self):
        asyncio.ensure_future(self.download_service.clear_completed())
        asyncio.ensure_future(self._refresh_downloads())
