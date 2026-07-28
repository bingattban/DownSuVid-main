"""
Constants Configuration Module
"""

APP_NAME = "DownSuVid"
APP_VERSION = "1.0.0"

# Storage Directories
STORAGE_ROOT = "DownSuVid"
STORAGE_CONFIG = "Config"
STORAGE_DATABASE = "Database"
STORAGE_DOWNLOADS = "Downloads"
STORAGE_VIDEOS = "Videos"
STORAGE_SUBTITLES = "Subtitles"
STORAGE_AUDIO = "Audio"
STORAGE_TEMP = "Temp"
STORAGE_CACHE = "Cache"
STORAGE_MODELS = "Models"
STORAGE_PACKAGES = "Packages"

# Database
DATABASE_NAME = "downsuviid.db"
DATABASE_VERSION = 1

# Settings Limits
MAX_FILE_SIZE = 1024 * 1024 * 1024 * 2  # 2GB
MIN_FREE_SPACE = 1024 * 1024 * 200      # 200MB
MAX_PARALLEL_DOWNLOADS = 5

# Supported Values
SUPPORTED_VIDEO_QUALITIES = ["1080p", "720p", "480p", "360p", "144p"]
SUBTITLE_FORMATS = ["srt", "vtt", "ass"]

# UI Colors (Hex)
COLOR_PRIMARY = "#009688"
COLOR_PRIMARY_DARK = "#00796B"
COLOR_ACCENT = "#FFC107"

# External Links
GITHUB_REPO = "https://github.com/downsuviid/DownSuVid"
WEBSITE_URL = "https://downsuviid.com"
