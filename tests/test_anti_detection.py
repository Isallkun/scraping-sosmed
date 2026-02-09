"""
Unit tests for anti-detection utilities.

Tests the anti-detection utilities that help avoid bot detection:
- Random user agent selection
- Random viewport size generation
- Human-like delays with random jitter

Validates Requirements: 1.4, 10.3
"""

import time
import pytest
from scraper.utils.anti_detection import AntiDetection, USER_AGENTS, VIEWPORT_SIZES


class TestGetRandomUserAgent:
    """Tests for get_random_user_agent() method."""
    
    def test_returns_string(self):
        """Test that get_random_user_agent returns a string."""
        ua = AntiDetection.get_random_user_agent()
        assert isinstance(ua, str)
    
    def test_returns_non_empty_string(self):
        """Test that the returned user agent is not empty."""
        ua = AntiDetection.get_random_user_agent()
        assert len(ua) > 0
    
    def test_returns_valid_user_agent(self):
        """Test that the returned user agent is from the predefined list."""
        ua = AntiDetection.get_random_user_agent()
        assert ua in USER_AGENTS
    
    def test_contains_mozilla(self):
        """Test that all user agents contain 'Mozilla' (standard format)."""
        ua = AntiDetection.get_random_user_agent()
        assert "Mozilla" in ua
    
    def test_randomization(self):
        """Test that multiple calls can return different user agents."""
        # Generate 20 user agents
        user_agents = [AntiDetection.get_random_user_agent() for _ in range(20)]
        
        # With 18 different user agents available, we should see some variety
        # in 20 calls (not all the same)
        unique_agents = set(user_agents)
        assert len(unique_agents) > 1, "Expected some randomization in user agents"
    
    def test_all_user_agents_valid(self):
        """Test that all predefined user agents are valid format."""
        for ua in USER_AGENTS:
            assert isinstance(ua, str)
            assert len(ua) > 50  # User agents should be reasonably long
            assert "Mozilla" in ua
            # Should contain browser identifier
            assert any(browser in ua for browser in ["Chrome", "Firefox", "Safari", "Edg"])


class TestGetRandomViewport:
    """Tests for get_random_viewport() method."""
    
    def test_returns_tuple(self):
        """Test that get_random_viewport returns a tuple."""
        viewport = AntiDetection.get_random_viewport()
        assert isinstance(viewport, tuple)
    
    def test_returns_two_elements(self):
        """Test that the viewport tuple has exactly 2 elements."""
        viewport = AntiDetection.get_random_viewport()
        assert len(viewport) == 2
    
    def test_returns_integers(self):
        """Test that both width and height are integers."""
        width, height = AntiDetection.get_random_viewport()
        assert isinstance(width, int)
        assert isinstance(height, int)
    
    def test_returns_valid_viewport(self):
        """Test that the returned viewport is from the predefined list."""
        viewport = AntiDetection.get_random_viewport()
        assert viewport in VIEWPORT_SIZES
    
    def test_reasonable_dimensions(self):
        """Test that viewport dimensions are reasonable for desktop browsers."""
        width, height = AntiDetection.get_random_viewport()
        # Desktop viewports should be at least 1280x720 and at most 2560x1600
        assert 1280 <= width <= 2560
        assert 720 <= height <= 1600
    
    def test_width_greater_than_height(self):
        """Test that width is greater than height (landscape orientation)."""
        width, height = AntiDetection.get_random_viewport()
        assert width > height, "Desktop viewports should be landscape (width > height)"
    
    def test_randomization(self):
        """Test that multiple calls can return different viewports."""
        # Generate 20 viewports
        viewports = [AntiDetection.get_random_viewport() for _ in range(20)]
        
        # With 10 different viewport sizes available, we should see some variety
        unique_viewports = set(viewports)
        assert len(unique_viewports) > 1, "Expected some randomization in viewports"
    
    def test_all_viewports_valid(self):
        """Test that all predefined viewports are valid."""
        for width, height in VIEWPORT_SIZES:
            assert isinstance(width, int)
            assert isinstance(height, int)
            assert width > 0
            assert height > 0
            assert width > height  # Landscape orientation


class TestHumanLikeDelay:
    """Tests for human_like_delay() method."""
    
    def test_default_delay_range(self):
        """Test that default delay is between 1 and 3 seconds."""
        start = time.time()
        AntiDetection.human_like_delay()
        elapsed = time.time() - start
        
        # Allow small overhead for function execution
        assert 1.0 <= elapsed <= 3.1, f"Expected delay between 1-3s, got {elapsed:.2f}s"
    
    def test_custom_delay_range(self):
        """Test that custom delay range is respected."""
        min_sec = 0.1
        max_sec = 0.2
        
        start = time.time()
        AntiDetection.human_like_delay(min_sec, max_sec)
        elapsed = time.time() - start
        
        # Allow small overhead
        assert min_sec <= elapsed <= max_sec + 0.1, \
            f"Expected delay between {min_sec}-{max_sec}s, got {elapsed:.2f}s"
    
    def test_zero_delay(self):
        """Test that zero delay works (min=0, max=0)."""
        start = time.time()
        AntiDetection.human_like_delay(0.0, 0.0)
        elapsed = time.time() - start
        
        # Should be very close to 0, allow small overhead
        assert elapsed < 0.1, f"Expected near-zero delay, got {elapsed:.2f}s"
    
    def test_randomization(self):
        """Test that delays are randomized (not always the same)."""
        delays = []
        
        # Measure 10 delays with a narrow range to make differences visible
        for _ in range(10):
            start = time.time()
            AntiDetection.human_like_delay(0.05, 0.15)
            elapsed = time.time() - start
            delays.append(round(elapsed, 3))
        
        # We should see some variation in the delays
        unique_delays = set(delays)
        assert len(unique_delays) > 1, "Expected some randomization in delays"
    
    def test_negative_min_raises_error(self):
        """Test that negative min_sec raises ValueError."""
        with pytest.raises(ValueError, match="must be non-negative"):
            AntiDetection.human_like_delay(-1.0, 2.0)
    
    def test_negative_max_raises_error(self):
        """Test that negative max_sec raises ValueError."""
        with pytest.raises(ValueError, match="must be non-negative"):
            AntiDetection.human_like_delay(1.0, -2.0)
    
    def test_min_greater_than_max_raises_error(self):
        """Test that min_sec > max_sec raises ValueError."""
        with pytest.raises(ValueError, match="min_sec must be less than or equal to max_sec"):
            AntiDetection.human_like_delay(5.0, 2.0)
    
    def test_equal_min_max(self):
        """Test that equal min and max values work (fixed delay)."""
        delay_value = 0.1
        
        start = time.time()
        AntiDetection.human_like_delay(delay_value, delay_value)
        elapsed = time.time() - start
        
        # Should be very close to the specified value
        assert abs(elapsed - delay_value) < 0.05, \
            f"Expected delay ~{delay_value}s, got {elapsed:.2f}s"


class TestAntiDetectionIntegration:
    """Integration tests for anti-detection utilities."""
    
    def test_all_methods_work_together(self):
        """Test that all anti-detection methods can be called in sequence."""
        # This simulates a typical usage pattern
        ua = AntiDetection.get_random_user_agent()
        viewport = AntiDetection.get_random_viewport()
        
        assert isinstance(ua, str)
        assert len(ua) > 0
        assert isinstance(viewport, tuple)
        assert len(viewport) == 2
        
        # Small delay to verify it doesn't raise errors
        start = time.time()
        AntiDetection.human_like_delay(0.05, 0.1)
        elapsed = time.time() - start
        assert 0.05 <= elapsed <= 0.15
    
    def test_multiple_sessions_have_different_signatures(self):
        """Test that multiple 'sessions' have different anti-detection signatures."""
        # Simulate 5 different scraping sessions
        sessions = []
        for _ in range(5):
            session = {
                'user_agent': AntiDetection.get_random_user_agent(),
                'viewport': AntiDetection.get_random_viewport()
            }
            sessions.append(session)
        
        # Check that we have some variety across sessions
        user_agents = [s['user_agent'] for s in sessions]
        viewports = [s['viewport'] for s in sessions]
        
        # With randomization, we should see some different values
        # (not all sessions identical)
        assert len(set(user_agents)) > 1 or len(set(viewports)) > 1, \
            "Expected some variation across sessions"
