"""
Settings Screen Module
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineListItem
from kivy.clock import Clock
import asyncio

from app.utils.logger import LoggerMixin
from app.services.settings.settings_service import SettingsService
from app.services.storage.storage_service import StorageService

class SettingsScreen(MDScreen, LoggerMixin):
    """Screen for application settings"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_service = SettingsService()
        self.storage_service = StorageService()
    
    def on_enter(self):
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self._load_settings()))
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self._load_storage_info()))
    
    async def _load_settings(self):
        try:
            theme = await self.settings_service.get_theme()
            Clock.schedule_once(lambda dt: self._update_settings_ui(theme))
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
    
    def _update_settings_ui(self, theme: str):
        self.ids.dark_mode_switch.active = (theme == 'dark')
    
    async def _load_storage_info(self):
        try:
            stats = await self.storage_service.get_storage_stats()
            Clock.schedule_once(
                lambda dt: setattr(
                    self.ids.storage_info, 'text', f"المساحة المستخدمة: {stats.get('used_space', 0)} MB"
                )
            )
        except Exception as e:
            self.logger.error(f"Failed to load storage info: {e}")
    
    def toggle_theme(self):
        is_dark = self.ids.dark_mode_switch.active
        theme = 'dark' if is_dark else 'light'
        asyncio.ensure_future(self.settings_service.set_theme(theme))
        
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark" if is_dark else "Light"
