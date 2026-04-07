"""
Performance History Management for LLM Task Router
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class PerformanceHistory:
    """
    Encapsulates logic for recording and retrieving model performance history.
    """

    def __init__(self):
        super().__init__()
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}

    def record_performance(
        self, model_name: str, latency_ms: int, tokens_used: int, cost: Optional[float]
    ):
        """Record performance data for learning."""
        if model_name not in self.performance_history:
            self.performance_history[model_name] = []

        self.performance_history[model_name].append(
            {
                "timestamp": datetime.utcnow(),
                "latency_ms": latency_ms,
                "tokens_used": tokens_used,
                "cost": cost,
                "throughput": (
                    tokens_used / (latency_ms / 1000) if latency_ms > 0 else 0
                ),
            }
        )

        # Keep only last 100 records per model
        if len(self.performance_history[model_name]) > 100:
            self.performance_history[model_name] = self.performance_history[model_name][
                -100:
            ]

    def get_history(self, model_name: str) -> List[Dict[str, Any]]:
        """Get performance history for a model."""
        return self.performance_history.get(model_name, [])
