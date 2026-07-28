"""
Download Service Module
"""

import os
import asyncio
import uuid
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.utils.file_utils import FileUtils
from app.domain.entities.download import (
    Download, DownloadStatus, VideoInfo, 
    SubtitleInfo, SubtitleStatus, DownloadProgress
)
from app.providers.downloader.ytdlp_provider import YTDLPProvider
from app.providers.ffmpeg.ffmpeg_provider import FFmpegProvider


class DownloadService(LoggerMixin):
    """Service for managing downloads"""
    
    def __init__(self):
        self.ytdlp_provider = YTDLPProvider()
        self.ffmpeg_provider = FFmpegProvider()
        self.active_downloads: Dict[str, Download] = {}
        self.download_queue: List[str] = []
        self.max_parallel = 3
        self._processing = False
        self.logger.info("DownloadService initialized")
    
    async def create_download(self, url: str) -> Optional[Download]:
        try:
            download_id = str(uuid.uuid4())
            download = Download(id=download_id, url=url, status=DownloadStatus.PENDING)
            
            self.active_downloads[download_id] = download
            self.download_queue.append(download_id)
            
            if not self._processing:
                asyncio.create_task(self._process_queue())
            
            self.logger.info(f"Download created: {download_id}")
            return download
        except Exception as e:
            self.logger.error(f"Failed to create download: {e}")
            return None
    
    async def analyze_url(self, url: str) -> Optional[VideoInfo]:
        try:
            info = await self.ytdlp_provider.extract_info(url)
            if not info: return None
            
            video_info = VideoInfo(
                url=url,
                title=info.get('title'),
                thumbnail_url=info.get('thumbnail'),
                uploader=info.get('uploader'),
                duration=info.get('duration'),
                website=info.get('extractor'),
                description=info.get('description'),
            )
            
            formats = await self.ytdlp_provider.get_video_formats(url)
            video_info.formats = formats
            video_info.qualities = [f['quality'] for f in formats]
            
            subtitles = await self.ytdlp_provider.get_available_subtitles(url)
            video_info.subtitle_languages = [s['language'] for s in subtitles]
            
            return video_info
        except Exception as e:
            self.logger.error(f"Failed to analyze URL: {e}")
            return None
    
    async def start_download(self, download_id: str, quality: str = "720p", download_subtitle: bool = True) -> bool:
        try:
            download = self.active_downloads.get(download_id)
            if not download:
                self.logger.error(f"Download not found: {download_id}")
                return False
            
            download.status = DownloadStatus.DOWNLOADING
            download.quality = quality
            
            asyncio.create_task(self._download_video(download, quality, download_subtitle))
            return True
        except Exception as e:
            self.logger.error(f"Failed to start download: {e}")
            return False
    
    async def _download_video(self, download: Download, quality: str, download_subtitle: bool):
        try:
            output_path = str(FileUtils.get_video_path())
            FileUtils.ensure_directory(output_path)
            
            def progress_hook(progress_data: dict):
                self._update_progress(download, progress_data)
            
            success = await self.ytdlp_provider.download_video(
                download.url, output_path, quality, progress_hook
            )
            
            if success:
                download.status = DownloadStatus.COMPLETED
                download.completed_at = datetime.now()
                
                if download_subtitle:
                    download.subtitle_status = SubtitleStatus.DOWNLOADING
                    asyncio.create_task(self._download_subtitles(download))
                
                self.logger.info(f"Download completed: {download.id}")
            else:
                download.status = DownloadStatus.FAILED
                download.error_message = "Download failed"
                
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            download.status = DownloadStatus.FAILED
            download.error_message = str(e)
    
    def _update_progress(self, download: Download, progress_data: dict):
        if progress_data.get('status') == 'downloading':
            downloaded = progress_data.get('downloaded_bytes', 0)
            total = progress_data.get('total_bytes', 0) or progress_data.get('total_bytes_estimate', 0)
            speed = progress_data.get('speed', 0)
            
            download.progress.downloaded_bytes = downloaded
            download.progress.total_bytes = total
            download.progress.speed_bytes = speed
            
            if total:
                download.progress.percentage = (downloaded / total) * 100
            
            if speed:
                download.progress.speed = f"{FileUtils.format_file_size(int(speed))}/s"
            
            eta = progress_data.get('eta')
            if eta:
                download.progress.eta = eta
    
    async def _download_subtitles(self, download: Download):
        try:
            subtitles = await self.ytdlp_provider.get_available_subtitles(download.url)
            arabic_subs = [s for s in subtitles if s['language'].lower() in ['ar', 'ara', 'arabic']]
            
            if arabic_subs:
                sub_path = await self.ytdlp_provider.download_subtitle(
                    download.url, 'ar', str(FileUtils.get_subtitle_path())
                )
                if sub_path:
                    download.subtitle_status = SubtitleStatus.COMPLETED
                    download.subtitle_path = sub_path
                    self.logger.info(f"Arabic subtitle downloaded for {download.id}")
                else:
                    download.subtitle_status = SubtitleStatus.FAILED
            else:
                download.subtitle_status = SubtitleStatus.NONE
                
        except Exception as e:
            self.logger.error(f"Subtitle download error: {e}")
            download.subtitle_status = SubtitleStatus.FAILED
    
    async def pause_download(self, download_id: str) -> bool:
        download = self.active_downloads.get(download_id)
        if download and download.status == DownloadStatus.DOWNLOADING:
            download.status = DownloadStatus.PAUSED
            return True
        return False
    
    async def resume_download(self, download_id: str) -> bool:
        download = self.active_downloads.get(download_id)
        if download and download.status == DownloadStatus.PAUSED:
            return await self.start_download(download_id, download.quality)
        return False
    
    async def cancel_download(self, download_id: str) -> bool:
        download = self.active_downloads.get(download_id)
        if download:
            download.status = DownloadStatus.CANCELLED
            if download_id in self.download_queue:
                self.download_queue.remove(download_id)
            return True
        return False
    
    async def retry_download(self, download_id: str) -> bool:
        download = self.active_downloads.get(download_id)
        if download and download.can_retry():
            download.retry_count += 1
            return await self.start_download(download_id, download.quality)
        return False
    
    async def delete_download(self, download_id: str) -> bool:
        download = self.active_downloads.get(download_id)
        if download:
            if download.file_path and os.path.exists(download.file_path):
                os.remove(download.file_path)
            if download.subtitle_path and os.path.exists(download.subtitle_path):
                os.remove(download.subtitle_path)
            
            del self.active_downloads[download_id]
            if download_id in self.download_queue:
                self.download_queue.remove(download_id)
            return True
        return False
    
    async def _process_queue(self):
        self._processing = True
        while self.download_queue:
            active_count = sum(1 for d in self.active_downloads.values() if d.status == DownloadStatus.DOWNLOADING)
            if active_count >= self.max_parallel:
                await asyncio.sleep(1)
                continue
            
            download_id = self.download_queue.pop(0)
            download = self.active_downloads.get(download_id)
            if download and download.status == DownloadStatus.PENDING:
                await self.start_download(download_id)
            
            await asyncio.sleep(0.5)
        self._processing = False
    
    async def get_downloads(self) -> List[Download]:
        return list(self.active_downloads.values())
    
    async def get_download(self, download_id: str) -> Optional[Download]:
        return self.active_downloads.get(download_id)
    
    async def get_queue_size(self) -> int:
        return len(self.download_queue)
    
    async def clear_completed(self):
        completed_ids = [d_id for d_id, d in self.active_downloads.items() if d.status in [DownloadStatus.COMPLETED, DownloadStatus.CANCELLED]]
        for d_id in completed_ids:
            del self.active_downloads[d_id]
    
    async def set_max_parallel(self, count: int):
        self.max_parallel = max(1, min(count, 10))
