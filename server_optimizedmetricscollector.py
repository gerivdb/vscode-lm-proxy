"""
Automatically extracted OptimizedMetricsCollector class
"""


class OptimizedMetricsCollector:
    """High-performance metrics collection with minimal overhead"""

    def __init__(self):
        super().__init__()
        self.metrics = {}
        self._lock = asyncio.Lock()
        self._buffer = []
        self._buffer_size = 1000
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._start_time = time.time()

    async def initialize(self):
        """Initialize metrics collector"""
        logger.info("OptimizedMetricsCollector initialized")
        return True

    async def close(self):
        """Close metrics collector"""
        self._executor.shutdown(wait=True)
        logger.info("OptimizedMetricsCollector closed")
        return True

    async def record_request(
        self, model_name: str, latency_ms: int, tokens: int, cost: Optional[float]
    ):
        """Record request metrics with buffering for performance"""
        async with self._lock:
            self._buffer.append(
                {
                    "model": model_name,
                    "latency": latency_ms,
                    "tokens": tokens,
                    "cost": cost,
                    "timestamp": time.time(),
                }
            )

            if len(self._buffer) >= self._buffer_size:
                await self._flush_buffer()

    async def _flush_buffer(self):
        """Flush metrics buffer to storage"""
        if not self._buffer:
            return

        buffer_copy = self._buffer.copy()
        self._buffer.clear()

        # Process in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._process_metrics, buffer_copy)

    def _process_metrics(self, metrics_data):
        """Process metrics in thread pool"""
        try:
            for metric in metrics_data:
                model = metric["model"]
                if model not in self.metrics:
                    self.metrics[model] = {
                        "total_requests": 0,
                        "total_latency": 0,
                        "total_tokens": 0,
                        "total_cost": 0,
                        "avg_latency": 0,
                        "avg_tokens": 0,
                        "avg_cost": 0,
                    }

                self.metrics[model]["total_requests"] += 1
                self.metrics[model]["total_latency"] += metric["latency"]
                self.metrics[model]["total_tokens"] += metric["tokens"]
                if metric["cost"]:
                    self.metrics[model]["total_cost"] += metric["cost"]

                # Update averages
                req_count = self.metrics[model]["total_requests"]
                self.metrics[model]["avg_latency"] = (
                    self.metrics[model]["total_latency"] / req_count
                )
                self.metrics[model]["avg_tokens"] = (
                    self.metrics[model]["total_tokens"] / req_count
                )
                if self.metrics[model]["total_cost"] > 0:
                    self.metrics[model]["avg_cost"] = (
                        self.metrics[model]["total_cost"] / req_count
                    )

        except Exception as e:
            logger.error(f"Metrics processing error: {e}")

    async def get_metrics(self, model_name: Optional[str] = None):
        """Get metrics for specific model or all models"""
        await self._flush_buffer()  # Ensure latest data

        if model_name:
            return self.metrics.get(model_name, {})
        return self.metrics

    async def get_system_metrics(self):
        """Get system-wide metrics"""
        await self._flush_buffer()

        total_requests = sum(
            model_data["total_requests"] for model_data in self.metrics.values()
        )
        total_cost = sum(
            model_data["total_cost"] for model_data in self.metrics.values()
        )

        return {
            "uptime": time.time() - self._start_time,
            "total_requests": total_requests,
            "total_cost": total_cost,
            "active_models": len(self.metrics),
        }
