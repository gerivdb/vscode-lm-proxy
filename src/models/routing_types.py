"""
Types for Routing Decisions and Query Results
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RoutingDecision:
    """Decision made by the router for a specific query"""

    selected_model: str
    confidence_score: float
    reasoning: str
    alternatives: Optional[List[str]] = None
    estimated_latency: int = 0
    estimated_cost: float = 0.0


@dataclass
class QueryResult:
    """Result of a routed query"""

    content: str
    model_used: str
    tokens_used: int
    latency_ms: int
    cost: Optional[float] = None
    routing_decision: Optional[RoutingDecision] = None
