"""
Dialogs Module
"""

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

from app.utils.logger import LoggerMixin

class DialogManager(LoggerMixin):
    """Manager for application dialogs"""
    
    @staticmethod
    def show_error_dialog(title: str = "خطأ", message: str = "حدث خطأ غير متوقع", callback=None) -> MDDialog:
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDFlatButton(text="موافق", on_release=lambda x: dialog.dismiss())]
        )
        if callback: dialog.bind(on_dismiss=callback)
        dialog.open()
        return dialog
    
    @staticmethod
    def show_success_dialog(title: str = "تم بنجاح", message: str = "تمت العملية بنجاح", callback=None) -> MDDialog:
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDFlatButton(text="موافق", on_release=lambda x: dialog.dismiss())]
        )
        if callback: dialog.bind(on_dismiss=callback)
        dialog.open()
        return dialog
    
    @staticmethod
    def show_confirm_dialog(title: str = "تأكيد", message: str = "هل أنت متأكد؟", on_confirm=None, on_cancel=None) -> MDDialog:
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(text="إلغاء", on_release=lambda x: (dialog.dismiss(), on_cancel() if on_cancel else None)),
                MDRaisedButton(text="موافق", on_release=lambda x: (dialog.dismiss(), on_confirm() if on_confirm else None)),
            ]
        )
        dialog.open()
        return dialog
