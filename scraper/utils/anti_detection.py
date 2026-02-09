"""
Anti-detection utilities for web scraping.

This module provides utilities to avoid bot detection by social media platforms:
- Random user agent selection
- Random viewport size generation
- Human-like delays with random jitter

Validates Requirements: 1.4, 10.3
"""

import random
import time
from typing import Tuple


# List of valid browser user agents for randomization
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    
    # Firefox on Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
]


# Common viewport sizes (width, height) for desktop browsers
VIEWPORT_SIZES = [
    (1920, 1080),  # Full HD
    (1366, 768),   # Common laptop
    (1536, 864),   # Common laptop
    (1440, 900),   # MacBook Pro 13"
    (1680, 1050),  # MacBook Pro 15"
    (2560, 1440),  # 2K
    (1280, 720),   # HD
    (1600, 900),   # HD+
    (1920, 1200),  # WUXGA
    (2560, 1600),  # MacBook Pro 16"
]


class AntiDetection:
    """
    Utilities for avoiding bot detection by social media platforms.
    
    This class provides static methods for:
    - Random user agent selection
    - Random viewport size generation
    - Human-like delays with random jitter
    """
    
    @staticmethod
    def get_random_user_agent() -> str:
        """
        Return a random user agent string from the predefined list.
        
        This helps avoid detection by varying the browser signature across
        different scraping sessions.
        
        Returns:
            str: A valid browser user agent string
            
        Example:
            >>> ua = AntiDetection.get_random_user_agent()
            >>> assert "Mozilla" in ua
            >>> assert len(ua) > 50
        """
        return random.choice(USER_AGENTS)
    
    @staticmethod
    def get_random_viewport() -> Tuple[int, int]:
        """
        Return random viewport dimensions (width, height).
        
        This helps avoid detection by varying the browser window size across
        different scraping sessions, mimicking different devices and screen
        resolutions.
        
        Returns:
            Tuple[int, int]: A tuple of (width, height) in pixels
            
        Example:
            >>> width, height = AntiDetection.get_random_viewport()
            >>> assert 1280 <= width <= 2560
            >>> assert 720 <= height <= 1600
        """
        return random.choice(VIEWPORT_SIZES)
    
    @staticmethod
    def human_like_delay(min_sec: float = 1.0, max_sec: float = 3.0) -> None:
        """
        Sleep for a random duration to mimic human behavior.
        
        Introduces a random delay between min_sec and max_sec seconds to make
        scraping patterns less predictable and more human-like. This helps
        avoid detection by rate limiting systems and behavioral analysis.
        
        Args:
            min_sec: Minimum delay in seconds (default: 1.0)
            max_sec: Maximum delay in seconds (default: 3.0)
            
        Raises:
            ValueError: If min_sec > max_sec or if either value is negative
            
        Example:
            >>> import time
            >>> start = time.time()
            >>> AntiDetection.human_like_delay(0.5, 1.0)
            >>> elapsed = time.time() - start
            >>> assert 0.5 <= elapsed <= 1.1  # Allow small overhead
        """
        if min_sec < 0 or max_sec < 0:
            raise ValueError("Delay values must be non-negative")
        
        if min_sec > max_sec:
            raise ValueError("min_sec must be less than or equal to max_sec")
        
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
