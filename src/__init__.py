"""
LM Hack Proxy - Intelligent LLM Orchestration for ECOS CLI
"""

__version__ = "1.0.0"
__author__ = "ECOS CLI Team"
__description__ = "Intelligent LLM orchestration proxy for ECOS CLI integration"

from .agents.coordinator import AgentCoordinator
from .models.registry import ModelRegistry
from .models.router import TaskRouter
from .utils.monitoring.metrics import MetricsCollector

__all__ = ["ModelRegistry", "TaskRouter", "AgentCoordinator", "MetricsCollector"]
