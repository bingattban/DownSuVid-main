"""
About Screen Module
"""

from kivymd.uix.screen import MDScreen
from kivy.utils import platform
from app.utils.logger import LoggerMixin
from app.config.constants import APP_NAME, APP_VERSION, GITHUB_REPO, WEBSITE_URL

class AboutScreen(MDScreen, LoggerMixin):
    """About screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger.info("AboutScreen initialized")
    
    def open_github(self):
        self._open_url(GITHUB_REPO)
    
    def open_website(self):
        self._open_url(WEBSITE_URL)
    
    def send_email(self):
        self._open_url("mailto:support@downsuviid.com")
    
    def _open_url(self, url: str):
        try:
            if platform == 'android':
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                intent = Intent(Intent.ACTION_VIEW)
                intent.setData(Uri.parse(url))
                PythonActivity.mActivity.startActivity(intent)
            else:
                import webbrowser
                webbrowser.open(url)
            self.logger.info(f"Opening URL: {url}")
        except Exception as e:
            self.logger.error(f"Failed to open URL: {e}")
