import threading
import time
from logger_setup import get_logger

logger = get_logger()

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill_time = time.time()
        self.lock = threading.Lock()

    def refill(self):
        with self.lock:
            now = time.time()
            time_elapsed = now - self.last_refill_time
            tokens_to_add = time_elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill_time = now

    def consume(self, tokens):
        with self.lock:
            if tokens <= self.tokens:
                self.tokens -= 1
                return True
            else:
                return False