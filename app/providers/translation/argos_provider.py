"""
Argos Translate Provider Implementation
"""

import os
from typing import Optional, Callable, List, Dict
from app.utils.logger import LoggerMixin
from app.providers.translation.translation_provider import TranslationProvider


class ArgosProvider(TranslationProvider):
    """Argos Translate provider"""
    
    def __init__(self):
        super().__init__()
        self._installed_packages = {}
        self.logger.info("ArgosProvider created")
    
    async def initialize(self) -> bool:
        try:
            import argostranslate.package
            import argostranslate.translate
            self._argos_package = argostranslate.package
            self._argos_translate = argostranslate.translate
            
            self._argos_package.update_package_index()
            self._load_installed_packages()
            self.logger.info("Argos Translate initialized")
            return True
        except ImportError:
            self.logger.warning("Argos Translate not installed - Will be disabled on Android")
            return False
        except Exception as e:
            self.logger.error(f"Argos initialization failed: {e}")
            return False
    
    def _load_installed_packages(self):
        try:
            installed = self._argos_package.get_installed_packages()
            for pkg in installed:
                key = f"{pkg.from_code}_{pkg.to_code}"
                self._installed_packages[key] = pkg
        except Exception as e:
            self.logger.warning(f"Failed to load packages: {e}")
    
    async def is_available(self) -> bool:
        try:
            import argostranslate.package
            return True
        except ImportError:
            return False
    
    async def download_package(self, source_lang: str, target_lang: str, progress_callback: Optional[Callable] = None) -> bool:
        try:
            available_packages = self._argos_package.get_available_packages()
            target_package = next((pkg for pkg in available_packages if pkg.from_code == source_lang and pkg.to_code == target_lang), None)
            
            if not target_package:
                return False
            
            if progress_callback: await progress_callback(f"{source_lang}_{target_lang}", 0.0, 'downloading')
            download_path = target_package.download()
            
            if progress_callback: await progress_callback(f"{source_lang}_{target_lang}", 50.0, 'installing')
            self._argos_package.install_from_path(download_path)
            
            if progress_callback: await progress_callback(f"{source_lang}_{target_lang}", 100.0, 'completed')
            self._load_installed_packages()
            return True
        except Exception as e:
            self.logger.error(f"Failed to download package: {e}")
            return False
    
    async def delete_package(self, source_lang: str, target_lang: str) -> bool:
        try:
            key = f"{source_lang}_{target_lang}"
            if key in self._installed_packages:
                pkg = self._installed_packages[key]
                if hasattr(pkg, 'package_path'): os.remove(pkg.package_path)
                del self._installed_packages[key]
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete package: {e}")
            return False
    
    async def verify_package(self, source_lang: str, target_lang: str) -> bool:
        return await self.is_package_installed(source_lang, target_lang)
    
    async def translate(self, text: str, source_lang: str, target_lang: str = "ar") -> Optional[str]:
        try:
            key = f"{source_lang}_{target_lang}"
            if key not in self._installed_packages: return None
            return self._installed_packages[key].translate(text)
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            return None
    
    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str = "ar") -> List[Optional[str]]:
        return [await self.translate(t, source_lang, target_lang) for t in texts]
    
    async def detect_language(self, text: str) -> Optional[str]:
        try:
            arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06ff')
            return 'ar' if arabic_chars > len(text) * 0.3 else 'en'
        except Exception:
            return None
    
    async def get_available_packages(self) -> List[Dict]:
        try:
            packages = []
            for pkg in self._argos_package.get_available_packages():
                packages.append({
                    'id': f"argos_{pkg.from_code}_{pkg.to_code}", 'name': f"{pkg.from_name} → {pkg.to_name}",
                    'source_lang': pkg.from_code, 'target_lang': pkg.to_code, 'installed': await self.is_package_installed(pkg.from_code, pkg.to_code),
                })
            return packages
        except Exception as e:
            self.logger.error(f"Failed to get packages: {e}")
            return []
    
    async def get_installed_packages(self) -> List[Dict]:
        return [{'id': f"argos_{k}", 'source_lang': k.split('_')[0], 'target_lang': k.split('_')[1], 'installed': True} for k in self._installed_packages.keys() if len(k.split('_')) == 2]
    
    async def is_package_installed(self, source_lang: str, target_lang: str) -> bool:
        return f"{source_lang}_{target_lang}" in self._installed_packages
    
    async def get_disk_usage(self) -> int:
        return sum(os.path.getsize(pkg.package_path) for pkg in self._installed_packages.values() if hasattr(pkg, 'package_path') and os.path.exists(pkg.package_path))
