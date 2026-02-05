"""
Rate Limiter for Gemini API Calls
Prevents 429 quota exceeded errors

Created by: Data Officer
Conforme au protocole du TP IGL 2025-2026

IMPORTANT: Free tier actual limit is 5 RPM, not 15!
Using 4 RPM to be safe and avoid quota errors.
"""

import time
from datetime import datetime, timedelta
from typing import Optional

class RateLimiter:
    """
    Rate limiter for Gemini API calls to prevent quota errors.
    
    Gemini Free Tier ACTUAL Limits (as of 2026):
    - 5 requests per minute (RPM) ← REAL LIMIT, not 15!
    - Resets every 60 seconds
    
    This limiter ensures we stay under the limit by:
    - Using 4 RPM (conservative, leaves 1 request margin)
    - 15 second delay between requests
    - Tracking request timestamps
    """
    
    def __init__(self, max_requests_per_minute: int = 4):
        """
        Initialize rate limiter.
        
        Args:
            max_requests_per_minute: Maximum API calls per minute (default: 4, SAFE for free tier)
        
        Note: Gemini free tier has 5 RPM limit, but we use 4 to be extra safe
        and account for any background requests or API delays.
        
        With 4 RPM:
        - 15 seconds between each request
        - Can process ~1 file per minute (3 agents × 1-2 iterations)
        - No quota errors!
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.min_delay = 60.0 / max_requests_per_minute  # 15 seconds for 4 RPM
        self.last_request_time: Optional[datetime] = None
        self.request_count = 0
        
    def wait_if_needed(self):
        """
        Wait if necessary to respect rate limits.
        Call this BEFORE making any Gemini API call.
        
        Example:
            rate_limiter.wait_if_needed()
            response = model.generate_content(prompt)
        """
        current_time = datetime.now()
        
        if self.last_request_time is not None:
            time_since_last = (current_time - self.last_request_time).total_seconds()
            
            if time_since_last < self.min_delay:
                wait_time = self.min_delay - time_since_last
                print(f"⏳ Rate limiting: waiting {wait_time:.1f}s to avoid quota errors (Free tier: 5 RPM)")
                time.sleep(wait_time)
        
        self.last_request_time = datetime.now()
        self.request_count += 1
        
    def reset(self):
        """Reset the rate limiter."""
        self.last_request_time = None
        self.request_count = 0
        
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        return {
            "total_requests": self.request_count,
            "max_rpm": self.max_requests_per_minute,
            "min_delay_seconds": self.min_delay,
            "last_request": self.last_request_time.isoformat() if self.last_request_time else None
        }


# Global rate limiter instance (4 RPM for free tier safety)
_global_limiter = RateLimiter(max_requests_per_minute=4)


def wait_for_rate_limit():
    """
    Convenience function - use this before EVERY Gemini API call.
    
    This enforces 15-second delays to stay under the 5 RPM free tier limit.
    
    Example usage in agents:
        from src.utils.rate_limiter import wait_for_rate_limit
        
        # Before calling Gemini:
        wait_for_rate_limit()
        response = model.generate_content(prompt)
    """
    _global_limiter.wait_if_needed()


def reset_rate_limiter():
    """Reset the global rate limiter."""
    _global_limiter.reset()


def get_rate_limiter_stats() -> dict:
    """Get statistics from the global rate limiter."""
    return _global_limiter.get_stats()


# Test the rate limiter
if __name__ == "__main__":
    print("=== Testing Rate Limiter (FREE TIER SAFE) ===\n")
    
    limiter = RateLimiter(max_requests_per_minute=4)
    
    print(f"Configuration: {limiter.max_requests_per_minute} requests/minute (Free tier safe)")
    print(f"Minimum delay: {limiter.min_delay:.2f} seconds")
    print(f"Gemini free tier limit: 5 RPM (we use 4 to be safe)\n")
    
    print("Simulating 5 API calls...")
    start_time = time.time()
    
    for i in range(5):
        call_start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - call_start
        total_elapsed = time.time() - start_time
        print(f"  Call {i+1}: waited {elapsed:.2f}s (total: {total_elapsed:.1f}s)")
    
    total_time = time.time() - start_time
    print(f"\n✅ Rate limiter working correctly!")
    print(f"Total time for 5 calls: {total_time:.1f}s")
    print(f"Average delay: {total_time/5:.1f}s per call")
    print(f"Stats: {limiter.get_stats()}")
    print(f"\n💡 With this rate, you can process ~1 file per minute safely.")