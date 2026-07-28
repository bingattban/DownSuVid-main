"""
Custom Widgets Module
"""

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.metrics import dp
from kivy.animation import Animation

class DownloadCard(MDCard):
    """Custom card widget for download items"""
    title = StringProperty("")
    status = StringProperty("")
    progress = NumericProperty(0)
    speed = StringProperty("")
    eta = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.elevation = 5
        self.radius = [15]
        self.size_hint_y = None
        self.height = dp(140)
        self._build_ui()
    
    def _build_ui(self):
        self.title_label = MDLabel(
            text=self.title, font_style='Subtitle1', bold=True, theme_text_color='Primary'
        )
        self.add_widget(self.title_label)
        
        self.progress_bar = MDProgressBar(value=self.progress, max=100, type='determinate')
        self.add_widget(self.progress_bar)
        
        info_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), adaptive_height=True)
        self.status_label = MDLabel(text=self.status, font_style='Caption', theme_text_color='Secondary', size_hint_x=0.4)
        info_box.add_widget(self.status_label)
        
        self.speed_label = MDLabel(text=self.speed, font_style='Caption', theme_text_color='Secondary', size_hint_x=0.3, halign='center')
        info_box.add_widget(self.speed_label)
        
        self.eta_label = MDLabel(text=self.eta, font_style='Caption', theme_text_color='Secondary', size_hint_x=0.3, halign='right')
        info_box.add_widget(self.eta_label)
        
        self.add_widget(info_box)
    
    def on_title(self, instance, value): self.title_label.text = value
    def on_progress(self, instance, value): self.progress_bar.value = value
    def on_status(self, instance, value): self.status_label.text = value
    def on_speed(self, instance, value): self.speed_label.text = value
    def on_eta(self, instance, value): self.eta_label.text = value
    
    def fade_out(self, callback=None):
        anim = Animation(opacity=0, duration=0.5)
        if callback: anim.bind(on_complete=lambda *args: callback())
        anim.start(self)

class StorageInfoWidget(MDCard):
    """Widget for displaying storage information"""
    used_space = StringProperty("0 MB")
    free_space = StringProperty("0 MB")
    total_space = StringProperty("0 MB")
    usage_percentage = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.elevation = 5
        self.radius = [15]
        self.size_hint_y = None
        self.height = dp(160)
        self._build_ui()
    
    def _build_ui(self):
        title_label = MDLabel(text='مساحة التخزين', font_style='H6', bold=True, theme_text_color='Primary')
        self.add_widget(title_label)
        
        self.storage_bar = MDProgressBar(value=self.usage_percentage, max=100, type='determinate')
        self.add_widget(self.storage_bar)
        
        info_box = MDBoxLayout(orientation='vertical', spacing=dp(5), adaptive_height=True)
        self.used_label = MDLabel(text=f"المستخدم: {self.used_space}", font_style='Caption', theme_text_color='Secondary')
        info_box.add_widget(self.used_label)
        
        self.free_label = MDLabel(text=f"المتاح: {self.free_space}", font_style='Caption', theme_text_color='Secondary')
        info_box.add_widget(self.free_label)
        
        self.total_label = MDLabel(text=f"الإجمالي: {self.total_space}", font_style='Caption', theme_text_color='Secondary')
        info_box.add_widget(self.total_label)
        
        self.add_widget(info_box)
