import threading
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

class Bulkhead:
    """Bulkhead pattern implementation to limit concurrent executions"""
    
    def __init__(self, max_concurrent_calls: int = 10, max_wait_time: float = 30.0):
        """
        Initialize bulkhead
        
        Args:
            max_concurrent_calls: Maximum number of concurrent calls allowed
            max_wait_time: Maximum time to wait for a slot (seconds)
        """
        self.max_concurrent_calls = max_concurrent_calls
        self.max_wait_time = max_wait_time
        self.semaphore = threading.Semaphore(max_concurrent_calls)
        self._current_calls = 0
        self._lock = threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply bulkhead pattern"""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            acquired = self.semaphore.acquire(timeout=self.max_wait_time)
            
            if not acquired:
                logger.warning(f"Bulkhead limit reached for {func.__name__}")
                raise BulkheadException(
                    f"Too many concurrent calls to {func.__name__}. "
                    f"Max: {self.max_concurrent_calls}"
                )
            
            try:
                with self._lock:
                    self._current_calls += 1
                logger.debug(f"Executing {func.__name__} ({self._current_calls}/{self.max_concurrent_calls})")
                return func(*args, **kwargs)
            finally:
                with self._lock:
                    self._current_calls -= 1
                self.semaphore.release()
        
        return wrapper
    
    def get_available_slots(self) -> int:
        """Get number of available execution slots"""
        return self.max_concurrent_calls - self._current_calls


class BulkheadException(Exception):
    """Exception raised when bulkhead limit is exceeded"""
    pass