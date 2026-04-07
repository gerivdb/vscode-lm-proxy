"""
Metrics Collector
Real-time performance monitoring and analytics for LM Hack Proxy
"""

import asyncio
import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and analyzes performance metrics for the LM Hack Proxy
    """

    def __init__(self, retention_period: int = 3600):  # 1 hour default
        super().__init__()
        self.retention_period = retention_period
        self._initialized = False

        # Core metrics storage
        self.request_metrics: List[Dict[str, Any]] = []
        self.model_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.system_metrics: Dict[str, Any] = {}

        # Aggregated statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = time.time()

    async def initialize(self):
        """Initialize the metrics collector"""
        if self._initialized:
            return

        logger.info("Initializing Metrics Collector...")
        self.start_time = time.time()
        self._initialized = True

        # Start background cleanup task
        asyncio.create_task(self._cleanup_old_metrics())

        logger.info("Metrics Collector initialized")

    async def close(self):
        """Cleanup resources"""
        logger.info("Closing Metrics Collector...")

    async def record_request(
        self,
        model_name: str,
        latency_ms: int,
        tokens_used: int,
        cost: Optional[float] = None,
        success: bool = True,
        error_type: Optional[str] = None,
    ):
        """
        Record metrics for a single request

        Args:
            model_name: Name of the model used
            latency_ms: Response latency in milliseconds
            tokens_used: Number of tokens consumed
            cost: Cost of the request (if available)
            success: Whether the request was successful
            error_type: Type of error if request failed
        """

        timestamp = datetime.utcnow()

        metric = {
            "timestamp": timestamp,
            "model_name": model_name,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "cost": cost,
            "success": success,
            "error_type": error_type,
            "throughput": tokens_used / (latency_ms / 1000) if latency_ms > 0 else 0,
        }

        self.request_metrics.append(metric)
        self.total_requests += 1

        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

        # Update model-specific metrics
        await self._update_model_metrics(model_name, metric)

        # Keep only recent metrics
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.retention_period)
        self.request_metrics = [
            m for m in self.request_metrics if m["timestamp"] > cutoff_time
        ]

    async def _update_model_metrics(self, model_name: str, metric: Dict[str, Any]):
        """Update aggregated metrics for a specific model"""

        if model_name not in self.model_metrics:
            self.model_metrics[model_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_latency_ms": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_latency_ms": 0.0,
                "avg_tokens_per_request": 0.0,
                "avg_cost_per_request": 0.0,
                "success_rate": 1.0,
                "last_request_time": None,
                "peak_latency_ms": 0,
                "min_latency_ms": float("inf"),
            }

        model_stats = self.model_metrics[model_name]

        # Update counters
        model_stats["total_requests"] += 1
        model_stats["total_latency_ms"] += metric["latency_ms"]
        model_stats["total_tokens"] += metric["tokens_used"]

        if metric["cost"]:
            model_stats["total_cost"] += metric["cost"]

        if metric["success"]:
            model_stats["successful_requests"] += 1
        else:
            model_stats["failed_requests"] += 1

        # Update min/max latency
        model_stats["peak_latency_ms"] = max(
            model_stats["peak_latency_ms"], metric["latency_ms"]
        )
        model_stats["min_latency_ms"] = min(
            model_stats["min_latency_ms"], metric["latency_ms"]
        )

        # Update averages
        total_req = model_stats["total_requests"]
        model_stats["avg_latency_ms"] = model_stats["total_latency_ms"] / total_req
        model_stats["avg_tokens_per_request"] = model_stats["total_tokens"] / total_req

        if model_stats["total_cost"] > 0:
            model_stats["avg_cost_per_request"] = model_stats["total_cost"] / total_req

        # Update success rate
        model_stats["success_rate"] = model_stats["successful_requests"] / total_req

        # Update last request time
        model_stats["last_request_time"] = metric["timestamp"]

    async def get_metrics(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current metrics

        Args:
            model_name: Specific model to get metrics for, or None for all

        Returns:
            Metrics dictionary
        """

        if model_name:
            return dict(self.model_metrics.get(model_name, {}))
        else:
            return dict(self.model_metrics)

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics"""

        uptime = time.time() - self.start_time
        success_rate = self.successful_requests / max(self.total_requests, 1)

        # Calculate request rate (requests per second)
        request_rate = self.total_requests / max(uptime, 1)

        # Get recent metrics (last 5 minutes)
        recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
        recent_metrics = [
            m for m in self.request_metrics if m["timestamp"] > recent_cutoff
        ]

        recent_avg_latency = 0.0
        if recent_metrics:
            recent_avg_latency = sum(m["latency_ms"] for m in recent_metrics) / len(
                recent_metrics
            )

        return {
            "uptime_seconds": uptime,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "request_rate_per_second": request_rate,
            "recent_avg_latency_ms": recent_avg_latency,
            "active_models": len(self.model_metrics),
            "metrics_retention_period": self.retention_period,
        }

    async def get_performance_summary(
        self, time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get performance summary for the specified time window

        Args:
            time_window_minutes: Time window in minutes

        Returns:
            Performance summary
        """

        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

        window_metrics = [
            m for m in self.request_metrics if m["timestamp"] > cutoff_time
        ]

        if not window_metrics:
            return {
                "time_window_minutes": time_window_minutes,
                "total_requests": 0,
                "avg_latency_ms": 0.0,
                "success_rate": 0.0,
                "total_cost": 0.0,
            }

        total_requests = len(window_metrics)
        avg_latency = sum(m["latency_ms"] for m in window_metrics) / total_requests
        success_rate = sum(1 for m in window_metrics if m["success"]) / total_requests
        total_cost = sum(m["cost"] or 0 for m in window_metrics)

        return {
            "time_window_minutes": time_window_minutes,
            "total_requests": total_requests,
            "avg_latency_ms": round(avg_latency, 2),
            "success_rate": round(success_rate, 3),
            "total_cost": round(total_cost, 4),
            "requests_per_minute": round(total_requests / time_window_minutes, 2),
        }

    async def get_model_performance_ranking(
        self, metric: str = "avg_latency_ms"
    ) -> List[Dict[str, Any]]:
        """
        Get models ranked by performance metric

        Args:
            metric: Metric to rank by ('avg_latency_ms', 'success_rate', 'total_requests')

        Returns:
            Ranked list of models with their metrics
        """

        model_list = []
        for model_name, stats in self.model_metrics.items():
            model_list.append(
                {
                    "model_name": model_name,
                    "metric_value": stats.get(metric, 0),
                    **stats,
                }
            )

        # Sort by metric (ascending for latency, descending for success rate and requests)
        reverse_sort = metric in ["success_rate", "total_requests"]
        model_list.sort(key=lambda x: x["metric_value"], reverse=reverse_sort)

        return model_list

    async def export_metrics(self, filepath: str):
        """
        Export all metrics to a JSON file

        Args:
            filepath: Path to export file
        """

        export_data = {
            "export_time": datetime.utcnow().isoformat(),
            "system_metrics": await self.get_system_metrics(),
            "model_metrics": dict(self.model_metrics),
            "recent_requests": [
                {
                    "timestamp": m["timestamp"].isoformat(),
                    "model_name": m["model_name"],
                    "latency_ms": m["latency_ms"],
                    "tokens_used": m["tokens_used"],
                    "cost": m["cost"],
                    "success": m["success"],
                }
                for m in self.request_metrics[-1000:]  # Last 1000 requests
            ],
        }

        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2, default=str)
            logger.info(f"Metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")

    async def _cleanup_old_metrics(self):
        """Background task to cleanup old metrics"""
        while True:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes

                cutoff_time = datetime.utcnow() - timedelta(
                    seconds=self.retention_period
                )

                # Clean up request metrics
                initial_count = len(self.request_metrics)
                self.request_metrics = [
                    m for m in self.request_metrics if m["timestamp"] > cutoff_time
                ]

                removed_count = initial_count - len(self.request_metrics)
                if removed_count > 0:
                    logger.debug(f"Cleaned up {removed_count} old metrics")

            except Exception as e:
                logger.error(f"Error in metrics cleanup: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
