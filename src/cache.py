from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import logging
import os
import sys

# Adding the path of the current folder to PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from directory_state import DirectoryState

logger = logging.getLogger(__name__)

class ScanCache:
    def __init__(self, ttl_minutes: int = 5):
        self.cache: Dict[str, dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.lock = threading.Lock()
        self.states: Dict[str, DirectoryState] = {}

    def _is_cache_valid(self, path: str) -> bool:
        """Checks if the cache is valid - both in terms of time and the state of the folder"""
        if path not in self.cache or path not in self.states:
            return False

        cache_entry = self.cache[path]
        dir_state = self.states[path]

        if datetime.now() - cache_entry['timestamp'] >= self.ttl:
            logger.info(f"Cache expired for path: {path}")
            return False

        if not dir_state.is_valid():
            logger.info(f"Directory state changed for path: {path}")
            return False

        return True

    def get(self, path: str) -> Optional[List[dict]]:
        """Gets results from the cache if they are still valid"""
        with self.lock:
            if self._is_cache_valid(path):
                logger.info(f"Cache hit for path: {path}")
                return self.cache[path]['data']
            else:
                self.invalidate(path)
                return None

    def set(self, path: str, data: List[dict]):
        """Caches results and updates folder status"""
        with self.lock:
            self.cache[path] = {
                'data': data,
                'timestamp': datetime.now()
            }
            self.states[path] = DirectoryState(path)
            logger.info(f"Cached results for path: {path}")

    def invalidate(self, path: str):
        """Invalidates the cache for a specific path"""
        with self.lock:
            self.cache.pop(path, None)
            self.states.pop(path, None)
            logger.info(f"Invalidated cache for path: {path}")

    def clear(self):
        """Clears all cache"""
        with self.lock:
            self.cache.clear()
            self.states.clear()
            logger.info("Cleared entire cache")

    def get_stats(self):
        """Returns statistics about the cache"""
        return {
            "cache_size": len(self.cache),
            "cache_ttl_minutes": self.ttl.total_seconds() / 60
        }
