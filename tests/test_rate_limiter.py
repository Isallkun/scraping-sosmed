"""
Unit tests for the rate limiter module.

Tests the token bucket rate limiting implementation to ensure it correctly
enforces rate limits and handles various edge cases.
"""

import time
import pytest
import threading
from scraper.utils.rate_limiter import RateLimiter


class TestRateLimiterInitialization:
    """Test rate limiter initialization and validation."""
    
    def test_valid_initialization(self):
        """Test rate limiter initializes correctly with valid parameters."""
        limiter = RateLimiter(requests_per_minute=60)
        assert limiter.requests_per_minute == 60
        assert limiter.get_available_tokens() == 60.0
    
    def test_initialization_with_low_rate(self):
        """Test rate limiter works with low request rates."""
        limiter = RateLimiter(requests_per_minute=1)
        assert limiter.requests_per_minute == 1
        assert limiter.get_available_tokens() == 1.0
    
    def test_initialization_with_high_rate(self):
        """Test rate limiter works with high request rates."""
        limiter = RateLimiter(requests_per_minute=1000)
        assert limiter.requests_per_minute == 1000
        assert limiter.get_available_tokens() == 1000.0
    
    def test_invalid_requests_per_minute_zero(self):
        """Test rate limiter raises error for zero requests per minute."""
        with pytest.raises(ValueError, match="requests_per_minute must be a positive integer"):
            RateLimiter(requests_per_minute=0)
    
    def test_invalid_requests_per_minute_negative(self):
        """Test rate limiter raises error for negative requests per minute."""
        with pytest.raises(ValueError, match="requests_per_minute must be a positive integer"):
            RateLimiter(requests_per_minute=-10)


class TestRateLimiterBasicAcquisition:
    """Test basic token acquisition functionality."""
    
    def test_acquire_single_token(self):
        """Test acquiring a single token succeeds immediately."""
        limiter = RateLimiter(requests_per_minute=60)
        result = limiter.acquire()
        assert result is True
        # Should have one less token
        assert limiter.get_available_tokens() < 60.0
    
    def test_acquire_multiple_tokens_with_capacity(self):
        """Test acquiring multiple tokens when capacity is available."""
        limiter = RateLimiter(requests_per_minute=10)
        
        # Acquire 5 tokens
        for i in range(5):
            result = limiter.acquire()
            assert result is True
        
        # Should have 5 tokens remaining
        remaining = limiter.get_available_tokens()
        assert 4.5 <= remaining <= 5.5  # Allow small timing variance
    
    def test_acquire_all_tokens(self):
        """Test acquiring all available tokens."""
        limiter = RateLimiter(requests_per_minute=5)
        
        # Acquire all 5 tokens
        for i in range(5):
            result = limiter.acquire()
            assert result is True
        
        # Should have approximately 0 tokens remaining
        remaining = limiter.get_available_tokens()
        assert remaining < 1.0


class TestRateLimiterBlocking:
    """Test blocking behavior when tokens are exhausted."""
    
    def test_blocking_acquire_waits_for_token(self):
        """Test that acquire blocks when no tokens are available."""
        limiter = RateLimiter(requests_per_minute=60)  # 1 token per second
        
        # Exhaust all tokens
        for _ in range(60):
            limiter.acquire()
        
        # Next acquire should block and wait
        start_time = time.time()
        result = limiter.acquire()
        elapsed = time.time() - start_time
        
        assert result is True
        # Should have waited approximately 1 second (1 token per second)
        assert elapsed >= 0.9  # Allow some timing variance
        assert elapsed <= 1.5  # But not too much
    
    def test_non_blocking_acquire_returns_false(self):
        """Test non-blocking acquire returns False when no tokens available."""
        limiter = RateLimiter(requests_per_minute=60)
        
        # Exhaust all tokens
        for _ in range(60):
            limiter.acquire()
        
        # Non-blocking acquire should return False immediately
        start_time = time.time()
        result = limiter.acquire(blocking=False)
        elapsed = time.time() - start_time
        
        assert result is False
        assert elapsed < 0.1  # Should return almost immediately
    
    def test_acquire_with_timeout_succeeds(self):
        """Test acquire with timeout succeeds when token becomes available."""
        limiter = RateLimiter(requests_per_minute=60)  # 1 token per second
        
        # Exhaust all tokens
        for _ in range(60):
            limiter.acquire()
        
        # Acquire with 2 second timeout should succeed
        start_time = time.time()
        result = limiter.acquire(timeout=2.0)
        elapsed = time.time() - start_time
        
        assert result is True
        assert elapsed >= 0.9  # Waited for token
        assert elapsed <= 1.5
    
    def test_acquire_with_timeout_fails(self):
        """Test acquire with timeout fails when timeout is too short."""
        limiter = RateLimiter(requests_per_minute=6)  # 1 token per 10 seconds
        
        # Exhaust all tokens
        for _ in range(6):
            limiter.acquire()
        
        # Acquire with 0.5 second timeout should fail (need 10 seconds)
        start_time = time.time()
        result = limiter.acquire(timeout=0.5)
        elapsed = time.time() - start_time
        
        assert result is False
        assert elapsed >= 0.4  # Waited for timeout
        assert elapsed <= 0.7
    
    def test_acquire_with_negative_timeout_raises_error(self):
        """Test acquire with negative timeout raises ValueError."""
        limiter = RateLimiter(requests_per_minute=60)
        
        with pytest.raises(ValueError, match="timeout must be non-negative"):
            limiter.acquire(timeout=-1.0)


class TestRateLimiterTokenRefill:
    """Test token refill mechanism."""
    
    def test_tokens_refill_over_time(self):
        """Test that tokens are refilled at the correct rate."""
        limiter = RateLimiter(requests_per_minute=60)  # 1 token per second
        
        # Exhaust all tokens
        for _ in range(60):
            limiter.acquire()
        
        # Wait for 2 seconds
        time.sleep(2.0)
        
        # Should have approximately 2 tokens refilled
        tokens = limiter.get_available_tokens()
        assert tokens >= 1.8  # Allow timing variance
        assert tokens <= 2.5
    
    def test_tokens_dont_exceed_maximum(self):
        """Test that tokens don't exceed maximum capacity."""
        limiter = RateLimiter(requests_per_minute=60)
        
        # Wait for some time
        time.sleep(2.0)
        
        # Should still have maximum tokens (60)
        tokens = limiter.get_available_tokens()
        assert tokens <= 60.0
    
    def test_partial_token_accumulation(self):
        """Test that partial tokens accumulate correctly."""
        limiter = RateLimiter(requests_per_minute=120)  # 2 tokens per second
        
        # Exhaust all tokens
        for _ in range(120):
            limiter.acquire()
        
        # Wait for 0.5 seconds (should get 1 token)
        time.sleep(0.5)
        
        # Should have approximately 1 token
        tokens = limiter.get_available_tokens()
        assert tokens >= 0.8
        assert tokens <= 1.5


class TestRateLimiterReset:
    """Test rate limiter reset functionality."""
    
    def test_reset_restores_full_capacity(self):
        """Test that reset restores full token capacity."""
        limiter = RateLimiter(requests_per_minute=60)
        
        # Exhaust some tokens
        for _ in range(30):
            limiter.acquire()
        
        # Reset
        limiter.reset()
        
        # Should have full capacity again
        tokens = limiter.get_available_tokens()
        assert tokens == 60.0
    
    def test_reset_after_complete_exhaustion(self):
        """Test reset works after all tokens are exhausted."""
        limiter = RateLimiter(requests_per_minute=10)
        
        # Exhaust all tokens
        for _ in range(10):
            limiter.acquire()
        
        # Reset
        limiter.reset()
        
        # Should be able to acquire immediately
        result = limiter.acquire(blocking=False)
        assert result is True


class TestRateLimiterWaitTime:
    """Test wait time calculation."""
    
    def test_wait_time_when_tokens_available(self):
        """Test wait time is zero when tokens are available."""
        limiter = RateLimiter(requests_per_minute=60)
        wait_time = limiter.get_wait_time()
        assert wait_time == 0.0
    
    def test_wait_time_when_tokens_exhausted(self):
        """Test wait time is calculated correctly when tokens are exhausted."""
        limiter = RateLimiter(requests_per_minute=60)  # 1 token per second
        
        # Exhaust all tokens
        for _ in range(60):
            limiter.acquire()
        
        # Wait time should be approximately 1 second
        wait_time = limiter.get_wait_time()
        assert wait_time >= 0.9
        assert wait_time <= 1.1
    
    def test_wait_time_decreases_over_time(self):
        """Test that wait time decreases as time passes."""
        limiter = RateLimiter(requests_per_minute=60)
        
        # Exhaust all tokens
        for _ in range(60):
            limiter.acquire()
        
        # Get initial wait time
        wait_time_1 = limiter.get_wait_time()
        
        # Wait a bit
        time.sleep(0.5)
        
        # Wait time should be less now
        wait_time_2 = limiter.get_wait_time()
        assert wait_time_2 < wait_time_1


class TestRateLimiterThreadSafety:
    """Test thread safety of rate limiter."""
    
    def test_concurrent_acquisitions(self):
        """Test that concurrent acquisitions are handled correctly."""
        limiter = RateLimiter(requests_per_minute=60)
        successful_acquisitions = []
        
        def acquire_token():
            result = limiter.acquire(blocking=False)
            if result:
                successful_acquisitions.append(1)
        
        # Create 100 threads trying to acquire tokens
        threads = []
        for _ in range(100):
            thread = threading.Thread(target=acquire_token)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have acquired at most 60 tokens (the initial capacity)
        assert len(successful_acquisitions) <= 60
        assert len(successful_acquisitions) >= 55  # Allow some variance


class TestRateLimiterRateEnforcement:
    """Test that rate limiting actually enforces the specified rate."""
    
    def test_rate_enforcement_over_time(self):
        """Test that rate is enforced over a period of time."""
        limiter = RateLimiter(requests_per_minute=30)  # 0.5 tokens per second
        
        # Try to acquire 10 tokens
        start_time = time.time()
        for _ in range(10):
            limiter.acquire()
        elapsed = time.time() - start_time
        
        # With 30 requests per minute, 10 requests should take at least:
        # First 30 are immediate, then we need to wait
        # Since we start with 30 tokens, first 10 are immediate
        # So elapsed should be very small
        assert elapsed < 1.0
        
        # Now exhaust remaining tokens and try 5 more
        for _ in range(20):  # Exhaust remaining 20 tokens
            limiter.acquire()
        
        # Next 5 should require waiting
        start_time = time.time()
        for _ in range(5):
            limiter.acquire()
        elapsed = time.time() - start_time
        
        # 5 tokens at 0.5 tokens/sec = 10 seconds
        assert elapsed >= 9.0  # Allow timing variance
        assert elapsed <= 11.0


class TestRateLimiterEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_very_low_rate_limit(self):
        """Test rate limiter with very low rate (1 request per minute)."""
        limiter = RateLimiter(requests_per_minute=1)
        
        # First request should succeed immediately
        result = limiter.acquire(blocking=False)
        assert result is True
        
        # Second request should fail (non-blocking)
        result = limiter.acquire(blocking=False)
        assert result is False
    
    def test_repr_string(self):
        """Test string representation of rate limiter."""
        limiter = RateLimiter(requests_per_minute=60)
        repr_str = repr(limiter)
        
        assert "RateLimiter" in repr_str
        assert "requests_per_minute=60" in repr_str
        assert "tokens=" in repr_str
    
    def test_multiple_resets(self):
        """Test that multiple resets work correctly."""
        limiter = RateLimiter(requests_per_minute=10)
        
        # Acquire some tokens
        for _ in range(5):
            limiter.acquire()
        
        # Reset multiple times
        limiter.reset()
        limiter.reset()
        limiter.reset()
        
        # Should still have full capacity
        tokens = limiter.get_available_tokens()
        assert tokens == 10.0
