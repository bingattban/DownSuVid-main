"""
Subtitle Entity Module
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class SubtitleFormat(Enum):
    SRT = "srt"
    VTT = "vtt"
    ASS = "ass"
    SSA = "ssa"
    SUB = "sub"

class SubtitleSource(Enum):
    DOWNLOADED = "downloaded"
    EXTRACTED = "extracted"
    GENERATED = "generated"
    TRANSLATED = "translated"
    EMBEDDED = "embedded"

class SubtitlePriority(Enum):
    ARABIC_ORIGINAL = 1
    OTHER_TRANSLATED = 2
    GENERATED = 3

@dataclass
class Subtitle:
    id: Optional[str] = None
    language: str = ""
    language_name: str = ""
    format: SubtitleFormat = SubtitleFormat.SRT
    source: SubtitleSource = SubtitleSource.DOWNLOADED
    priority: SubtitlePriority = SubtitlePriority.OTHER_TRANSLATED
    
    file_path: Optional[str] = None
    content: Optional[str] = None
    original_content: Optional[str] = None
    
    is_auto_generated: bool = False
    confidence_score: Optional[float] = None
    word_count: int = 0
    character_count: int = 0
    
    original_language: Optional[str] = None
    translated_from: Optional[str] = None
    translation_engine: Optional[str] = None
    
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    has_timing_errors: bool = False
    has_encoding_errors: bool = False
    quality_score: Optional[float] = None
    
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def is_arabic(self) -> bool: return self.language.lower() in ['ar', 'ara', 'arabic', 'العربية']
    def needs_translation(self) -> bool: return not self.is_arabic()
    def get_file_extension(self) -> str: return self.format.value
    
    def parse_content(self) -> List[Dict]:
        if not self.content: return []
        try:
            if self.format == SubtitleFormat.SRT: return self._parse_srt(self.content)
            elif self.format == SubtitleFormat.VTT: return self._parse_vtt(self.content)
            elif self.format == SubtitleFormat.ASS: return self._parse_ass(self.content)
        except Exception: pass
        return []
    
    def _parse_srt(self, content: str) -> List[Dict]:
        entries = []
        for block in content.strip().split('\n\n'):
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    times = lines[1].split(' --> ')
                    entries.append({'start_time': self._time_to_seconds(times[0]), 'end_time': self._time_to_seconds(times[1]), 'text': '\n'.join(lines[2:])})
                except Exception: continue
        return entries
    
    def _parse_vtt(self, content: str) -> List[Dict]:
        entries = []
        lines = content.strip().split('\n')
        i = 0
        while i < len(lines):
            if '-->' in lines[i]:
                try:
                    times = lines[i].split(' --> ')
                    start, end = self._time_to_seconds(times[0]), self._time_to_seconds(times[1])
                    i += 1
                    text_lines = []
                    while i < len(lines) and lines[i].strip():
                        text_lines.append(lines[i])
                        i += 1
                    entries.append({'start_time': start, 'end_time': end, 'text': '\n'.join(text_lines)})
                except Exception: i += 1
            else: i += 1
        return entries
    
    def _parse_ass(self, content: str) -> List[Dict]:
        entries = []
        in_events = False
        for line in content.split('\n'):
            if '[Events]' in line:
                in_events = True
                continue
            if in_events and line.startswith('Dialogue:'):
                try:
                    parts = line.split(',', 9)
                    if len(parts) >= 9:
                        entries.append({'start_time': self._time_to_seconds(parts[1]), 'end_time': self._time_to_seconds(parts[2]), 'text': parts[9].strip()})
                except Exception: continue
        return entries
    
    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        time_str = time_str.strip().replace(',', '.')
        parts = time_str.split(':')
        if len(parts) == 3: return (int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2]))
        elif len(parts) == 2: return int(parts[0]) * 60 + float(parts[1])
        else: return float(parts[0])
    
    def to_srt_format(self) -> str:
        if not self.content: return ""
        srt_content = []
        for i, entry in enumerate(self.parse_content(), 1):
            srt_content.extend([f"{i}", f"{self._seconds_to_time(entry['start_time'])} --> {self._seconds_to_time(entry['end_time'])}", entry['text'], ""])
        return '\n'.join(srt_content)
    
    @staticmethod
    def _seconds_to_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')
