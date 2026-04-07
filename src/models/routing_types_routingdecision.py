"""
Automatically extracted RoutingDecision class
"""


class RoutingDecision:
    """Decision made by the router for a specific query"""

    selected_model: str
    confidence_score: float
    reasoning: str
    alternatives: Optional[List[str]] = None
    estimated_latency: int = 0
    estimated_cost: float = 0.0
