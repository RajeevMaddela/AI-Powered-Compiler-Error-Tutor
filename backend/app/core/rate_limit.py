import time
from collections import defaultdict
from threading import Lock

class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.history = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        with self.lock:
            # Purge timestamps outside the window
            timestamps = [t for t in self.history[key] if t > cutoff]
            if len(timestamps) >= self.max_requests:
                self.history[key] = timestamps
                return False
            timestamps.append(now)
            self.history[key] = timestamps
            return True

    def reset(self, key: str):
        with self.lock:
            if key in self.history:
                del self.history[key]

# Global instance for auth login attempts: max 5 attempts per 60 seconds per IP/email
login_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)

# Global instance for analyze requests: max 10 requests per 60 seconds per user
analyze_rate_limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)
