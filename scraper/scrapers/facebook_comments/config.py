"""Configuration management for Facebook Comment Crawler"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FBCommentConfig:
    """Facebook Comment Crawler configuration"""

    # Project paths - relative to scraping-sosmed root
    BASE_DIR = Path(__file__).parent.parent.parent.parent
    DATA_DIR = BASE_DIR / "data" / "facebook_comments"
    COOKIES_DIR = DATA_DIR / "cookies"
    EXPORTS_DIR = DATA_DIR / "exports"
    LOGS_DIR = DATA_DIR / "logs"

    # Facebook credentials (reuse existing env vars from scraping-sosmed)
    FB_EMAIL: str = os.getenv("FB_COMMENT_EMAIL", os.getenv("FACEBOOK_USERNAME", ""))
    FB_PASSWORD: str = os.getenv("FB_COMMENT_PASSWORD", os.getenv("FACEBOOK_PASSWORD", ""))

    # Crawler settings
    HEADLESS: bool = os.getenv("FB_COMMENT_HEADLESS", os.getenv("SCRAPER_HEADLESS", "true")).lower() == "true"
    MIN_DELAY: int = int(os.getenv("FB_COMMENT_MIN_DELAY", "2"))
    MAX_DELAY: int = int(os.getenv("FB_COMMENT_MAX_DELAY", "5"))
    SCROLL_PAUSE_TIME: int = int(os.getenv("FB_COMMENT_SCROLL_PAUSE_TIME", "2"))
    MAX_SCROLL_ATTEMPTS: int = int(os.getenv("FB_COMMENT_MAX_SCROLL_ATTEMPTS", "10"))
    REQUEST_TIMEOUT: int = int(os.getenv("FB_COMMENT_REQUEST_TIMEOUT", "30000"))

    # Export settings
    EXPORT_MODE: str = os.getenv("FB_COMMENT_EXPORT_MODE", "single")  # single or per-post
    EXPORT_FORMAT: str = os.getenv("FB_COMMENT_EXPORT_FORMAT", "csv")  # csv, excel, or json

    # Profile crawler settings
    MAX_POSTS_PER_PROFILE: int = int(os.getenv("FB_COMMENT_MAX_POSTS_PER_PROFILE", "50"))
    PROFILE_SCROLL_LIMIT: int = int(os.getenv("FB_COMMENT_PROFILE_SCROLL_LIMIT", "20"))

    # Logging
    LOG_LEVEL: str = os.getenv("FB_COMMENT_LOG_LEVEL", os.getenv("SCRAPER_LOG_LEVEL", "INFO"))

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist"""
        for directory in [cls.COOKIES_DIR, cls.EXPORTS_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.FB_EMAIL or not cls.FB_PASSWORD:
            return False
        return True

    @classmethod
    def get_cookies_path(cls, identifier: str = "default") -> Path:
        """Get path for cookies file"""
        return cls.COOKIES_DIR / f"cookies_{identifier}.json"

    @classmethod
    def get_export_path(cls, filename: str) -> Path:
        """Get path for export file"""
        return cls.EXPORTS_DIR / filename


# Ensure directories exist on import
FBCommentConfig.ensure_directories()
