"""
Automatically extracted ResponseCache class
"""


class ResponseCache:
    """High-performance LRU cache for API responses"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        super().__init__()
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._lock = asyncio.Lock()

    def _generate_key(self, prompt: str, model: str, options: Dict[str, Any]) -> str:
        """Generate cache key from request parameters"""
        key_data = f"{prompt}:{model}:{json.dumps(options, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    async def get(
        self, prompt: str, model: str, options: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        async with self._lock:
            key = self._generate_key(prompt, model, options)
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry["timestamp"] < self.ttl_seconds:
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    return entry["response"]
                else:
                    # Expired, remove
                    del self.cache[key]
            return None

    async def set(
        self, prompt: str, model: str, options: Dict[str, Any], response: Dict[str, Any]
    ):
        """Cache response with timestamp"""
        async with self._lock:
            key = self._generate_key(prompt, model, options)
            if key in self.cache:
                del self.cache[key]

            self.cache[key] = {"response": response, "timestamp": time.time()}

            # Evict least recently used if over capacity
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
