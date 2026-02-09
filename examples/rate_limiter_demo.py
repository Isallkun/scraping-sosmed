"""
Demo script showing how to use the RateLimiter class.

This script demonstrates various usage patterns for the rate limiter,
including basic usage, non-blocking mode, and integration with scraping.
"""

import time
from scraper.utils.rate_limiter import RateLimiter


def demo_basic_usage():
    """Demonstrate basic rate limiter usage."""
    print("=" * 60)
    print("Demo 1: Basic Usage")
    print("=" * 60)
    
    # Create a rate limiter allowing 30 requests per minute (1 every 2 seconds)
    limiter = RateLimiter(requests_per_minute=30)
    
    print(f"Rate limiter created: {limiter}")
    print(f"Available tokens: {limiter.get_available_tokens()}")
    
    # Make 5 requests
    print("\nMaking 5 requests...")
    for i in range(5):
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start
        print(f"Request {i+1}: waited {elapsed:.3f}s, "
              f"tokens remaining: {limiter.get_available_tokens():.2f}")
    
    print()


def demo_non_blocking():
    """Demonstrate non-blocking mode."""
    print("=" * 60)
    print("Demo 2: Non-Blocking Mode")
    print("=" * 60)
    
    # Create a rate limiter with low rate
    limiter = RateLimiter(requests_per_minute=6)  # 1 every 10 seconds
    
    print(f"Rate limiter created: {limiter}")
    
    # Exhaust all tokens
    print("\nExhausting all tokens...")
    for i in range(6):
        success = limiter.acquire(blocking=False)
        print(f"Request {i+1}: {'Success' if success else 'Failed'}")
    
    # Try one more (should fail)
    print("\nTrying one more request (non-blocking)...")
    success = limiter.acquire(blocking=False)
    print(f"Result: {'Success' if success else 'Failed (as expected)'}")
    
    wait_time = limiter.get_wait_time()
    print(f"Wait time for next token: {wait_time:.2f}s")
    
    print()


def demo_with_timeout():
    """Demonstrate timeout functionality."""
    print("=" * 60)
    print("Demo 3: Timeout Mode")
    print("=" * 60)
    
    limiter = RateLimiter(requests_per_minute=60)
    
    # Exhaust all tokens
    print("Exhausting all tokens...")
    for _ in range(60):
        limiter.acquire()
    
    print(f"Tokens remaining: {limiter.get_available_tokens():.2f}")
    
    # Try with short timeout (should fail)
    print("\nTrying to acquire with 0.5s timeout...")
    start = time.time()
    success = limiter.acquire(timeout=0.5)
    elapsed = time.time() - start
    print(f"Result: {'Success' if success else 'Timeout'}, elapsed: {elapsed:.2f}s")
    
    # Try with longer timeout (should succeed)
    print("\nTrying to acquire with 2s timeout...")
    start = time.time()
    success = limiter.acquire(timeout=2.0)
    elapsed = time.time() - start
    print(f"Result: {'Success' if success else 'Timeout'}, elapsed: {elapsed:.2f}s")
    
    print()


def demo_reset():
    """Demonstrate reset functionality."""
    print("=" * 60)
    print("Demo 4: Reset Functionality")
    print("=" * 60)
    
    limiter = RateLimiter(requests_per_minute=10)
    
    print(f"Initial tokens: {limiter.get_available_tokens():.2f}")
    
    # Use some tokens
    print("\nUsing 7 tokens...")
    for _ in range(7):
        limiter.acquire()
    
    print(f"Tokens after usage: {limiter.get_available_tokens():.2f}")
    
    # Reset
    print("\nResetting rate limiter...")
    limiter.reset()
    
    print(f"Tokens after reset: {limiter.get_available_tokens():.2f}")
    
    print()


def demo_scraping_simulation():
    """Simulate using rate limiter in a scraping scenario."""
    print("=" * 60)
    print("Demo 5: Scraping Simulation")
    print("=" * 60)
    
    # Simulate scraping with rate limiting
    limiter = RateLimiter(requests_per_minute=30)  # 30 requests per minute
    
    urls = [
        "https://example.com/post/1",
        "https://example.com/post/2",
        "https://example.com/post/3",
        "https://example.com/post/4",
        "https://example.com/post/5",
    ]
    
    print(f"Scraping {len(urls)} URLs with rate limit of 30 requests/minute")
    print()
    
    start_time = time.time()
    
    for i, url in enumerate(urls, 1):
        # Wait for rate limiter
        limiter.acquire()
        
        # Simulate scraping (in real code, this would be actual HTTP request)
        print(f"[{time.time() - start_time:.2f}s] Scraping {url}...")
        time.sleep(0.1)  # Simulate request time
        
        tokens_left = limiter.get_available_tokens()
        print(f"  -> Success! Tokens remaining: {tokens_left:.2f}")
    
    total_time = time.time() - start_time
    print(f"\nTotal time: {total_time:.2f}s")
    print(f"Average time per request: {total_time/len(urls):.2f}s")
    
    print()


def main():
    """Run all demos."""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  Rate Limiter Demo".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print("\n")
    
    demo_basic_usage()
    demo_non_blocking()
    demo_with_timeout()
    demo_reset()
    demo_scraping_simulation()
    
    print("=" * 60)
    print("All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
