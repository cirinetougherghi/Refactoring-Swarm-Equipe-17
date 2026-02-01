"""
Rate Limiter for Gemini API Calls
Prevents 429 quota exceeded errors

Created by: Data Officer
Conforme au protocole du TP IGL 2025-2026
"""

import time
from datetime import datetime, timedelta
from typing import Optional

class RateLimiter:
    """
    Rate limiter for Gemini API calls to prevent quota errors.
    
    Gemini Free Tier Limits:
    - 15 requests per minute (RPM)
    - 1 million tokens per day
    
    This limiter ensures we stay under the limit by:
    - Tracking request timestamps
    - Enforcing minimum delay between requests
    - Conservative rate (12 requests/minute to be safe)
    """
    
    def __init__(self, max_requests_per_minute: int = 12):
        """
        Initialize rate limiter.
        
        Args:
            max_requests_per_minute: Maximum API calls per minute (default: 12, conservative)
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.min_delay = 60.0 / max_requests_per_minute  # Seconds between requests
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
                print(f"⏳ Rate limiting: waiting {wait_time:.1f}s to avoid quota errors...")
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


# Global rate limiter instance
_global_limiter = RateLimiter()


def wait_for_rate_limit():
    """
    Convenience function - use this before EVERY Gemini API call.
    
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
    print("=== Testing Rate Limiter ===\n")
    
    limiter = RateLimiter(max_requests_per_minute=12)
    
    print(f"Configuration: {limiter.max_requests_per_minute} requests/minute")
    print(f"Minimum delay: {limiter.min_delay:.2f} seconds\n")
    
    print("Simulating 5 API calls...")
    for i in range(5):
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start
        print(f"  Call {i+1}: waited {elapsed:.2f}s")
    
    print(f"\n✅ Rate limiter working correctly!")
    print(f"Stats: {limiter.get_stats()}")