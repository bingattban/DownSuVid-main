"""
Download Entity Module
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class DownloadStatus(Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class SubtitleStatus(Enum):
    NONE = "none"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    TRANSLATING = "translating"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class VideoInfo:
    url: str
    title: Optional[str] = None
    thumbnail_url: Optional[str] = None
    uploader: Optional[str] = None
    duration: Optional[int] = None
    website: Optional[str] = None
    description: Optional[str] = None
    
    formats: List[Dict] = field(default_factory=list)
    qualities: List[str] = field(default_factory=list)
    audio_languages: List[str] = field(default_factory=list)
    subtitle_languages: List[str] = field(default_factory=list)
    
    estimated_size: Optional[int] = None
    estimated_size_formatted: Optional[str] = None


@dataclass
class SubtitleInfo:
    language: str
    language_name: str
    format: str = "srt"
    is_auto_generated: bool = False
    url: Optional[str] = None
    file_path: Optional[str] = None
    status: SubtitleStatus = SubtitleStatus.NONE
    original_language: Optional[str] = None
    translated_path: Optional[str] = None
    
    confidence_score: Optional[float] = None
    word_count: Optional[int] = None


@dataclass
class DownloadProgress:
    percentage: float = 0.0
    speed: Optional[str] = None
    speed_bytes: Optional[float] = None
    downloaded_bytes: int = 0
    total_bytes: int = 0
    eta: Optional[int] = None
    elapsed: Optional[int] = None
    
    def get_formatted_speed(self) -> str:
        if self.speed:
            return self.speed
        if self.speed_bytes:
            from app.utils.file_utils import FileUtils
            return f"{FileUtils.format_file_size(int(self.speed_bytes))}/s"
        return "0 B/s"
    
    def get_formatted_eta(self) -> str:
        if self.eta is None:
            return "--:--"
        minutes, seconds = divmod(self.eta, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"


@dataclass
class Download:
    id: str
    url: str
    title: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    file_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    
    status: DownloadStatus = DownloadStatus.PENDING
    subtitle_status: SubtitleStatus = SubtitleStatus.NONE
    progress: DownloadProgress = field(default_factory=DownloadProgress)
    
    format_id: Optional[str] = None
    quality: Optional[str] = None
    
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    video_info: Optional[VideoInfo] = None
    subtitles: List[SubtitleInfo] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    queue_position: int = 0
    priority: int = 0
    
    def get_remaining_size(self) -> int:
        return self.progress.total_bytes - self.progress.downloaded_bytes
    
    def is_completed(self) -> bool:
        return self.status == DownloadStatus.COMPLETED
    
    def is_active(self) -> bool:
        return self.status in [DownloadStatus.DOWNLOADING, DownloadStatus.PROCESSING]
    
    def can_resume(self) -> bool:
        return self.status == DownloadStatus.PAUSED
    
    def can_retry(self) -> bool:
        return (self.status == DownloadStatus.FAILED and self.retry_count < self.max_retries)
    
    def format_duration(self) -> str:
        if self.video_info and self.video_info.duration:
            minutes, seconds = divmod(self.video_info.duration, 60)
            hours, minutes = divmod(minutes, 60)
            if hours:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            return f"{minutes}:{seconds:02d}"
        return "--:--"
