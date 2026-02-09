"""
Rate limiter implementation using token bucket algorithm.

This module provides rate limiting functionality to respect platform API limits
and terms of service. The token bucket algorithm allows for burst traffic while
maintaining an average rate limit.

Requirements:
- 1.3: Rate limiting with configurable delay between requests
- 10.2: Respect platform API limits and terms of service
"""

import time
import threading
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter for controlling request frequency.
    
    The token bucket algorithm maintains a bucket of tokens that refills at a
    constant rate. Each request consumes one token. If no tokens are available,
    the request blocks until a token becomes available.
    
    Attributes:
        requests_per_minute (int): Maximum number of requests allowed per minute
        _tokens (float): Current number of tokens in the bucket
        _max_tokens (float): Maximum capacity of the bucket
        _refill_rate (float): Rate at which tokens are added (tokens per second)
        _last_refill (float): Timestamp of last token refill
        _lock (threading.Lock): Thread lock for thread-safe operations
    """
    
    def __init__(self, requests_per_minute: int):
        """
        Initialize rate limiter with specified requests per minute.
        
        Args:
            requests_per_minute: Maximum number of requests allowed per minute.
                                Must be a positive integer.
        
        Raises:
            ValueError: If requests_per_minute is not positive
        """
        if requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be a positive integer")
        
        self.requests_per_minute = requests_per_minute
        
        # Token bucket parameters
        self._max_tokens = float(requests_per_minute)
        self._tokens = float(requests_per_minute)  # Start with full bucket
        self._refill_rate = requests_per_minute / 60.0  # tokens per second
        self._last_refill = time.time()
        
        # Thread safety
        self._lock = threading.Lock()
    
    def _refill_tokens(self) -> None:
        """
        Refill tokens based on elapsed time since last refill.
        
        This method is called internally before each token acquisition to ensure
        the bucket is up-to-date with the current time.
        """
        now = time.time()
        elapsed = now - self._last_refill
        
        # Calculate tokens to add based on elapsed time
        tokens_to_add = elapsed * self._refill_rate
        
        # Add tokens but don't exceed maximum capacity
        self._tokens = min(self._max_tokens, self._tokens + tokens_to_add)
        self._last_refill = now
    
    def acquire(self, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire a token from the bucket, blocking until one is available.
        
        This method should be called before making a request. It will block
        (sleep) until a token is available, respecting the configured rate limit.
        
        Args:
            blocking: If True, block until a token is available. If False, return
                     immediately with success/failure status.
            timeout: Maximum time to wait for a token (in seconds). Only used if
                    blocking is True. None means wait indefinitely.
        
        Returns:
            bool: True if token was acquired, False if non-blocking and no token
                 available or timeout exceeded.
        
        Raises:
            ValueError: If timeout is negative
        """
        if timeout is not None and timeout < 0:
            raise ValueError("timeout must be non-negative")
        
        start_time = time.time()
        
        while True:
            with self._lock:
                self._refill_tokens()
                
                # If we have tokens available, consume one and return
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return True
                
                # If non-blocking, return immediately
                if not blocking:
                    return False
                
                # Calculate how long to wait for next token
                tokens_needed = 1.0 - self._tokens
                wait_time = tokens_needed / self._refill_rate
            
            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return False
                # Adjust wait time to not exceed timeout
                wait_time = min(wait_time, timeout - elapsed)
            
            # Sleep until next token should be available
            # Add small buffer to account for timing precision
            time.sleep(wait_time + 0.001)
    
    def reset(self) -> None:
        """
        Reset the rate limiter to initial state with full token bucket.
        
        This method can be used to clear any rate limiting state, for example
        when starting a new scraping session or after an error.
        """
        with self._lock:
            self._tokens = self._max_tokens
            self._last_refill = time.time()
    
    def get_available_tokens(self) -> float:
        """
        Get the current number of available tokens in the bucket.
        
        This method is primarily useful for monitoring and debugging.
        
        Returns:
            float: Current number of tokens available (0 to max_tokens)
        """
        with self._lock:
            self._refill_tokens()
            return self._tokens
    
    def get_wait_time(self) -> float:
        """
        Get the estimated wait time until next token is available.
        
        Returns:
            float: Estimated wait time in seconds. Returns 0 if tokens are
                  currently available.
        """
        with self._lock:
            self._refill_tokens()
            
            if self._tokens >= 1.0:
                return 0.0
            
            tokens_needed = 1.0 - self._tokens
            return tokens_needed / self._refill_rate
    
    def __repr__(self) -> str:
        """String representation of the rate limiter."""
        return (f"RateLimiter(requests_per_minute={self.requests_per_minute}, "
                f"tokens={self._tokens:.2f}/{self._max_tokens:.2f})")
