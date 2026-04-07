"""
Automatically extracted QueryResult class
"""


class QueryResult:
    """Result of a routed query"""

    content: str
    model_used: str
    tokens_used: int
    latency_ms: int
    cost: Optional[float] = None
    routing_decision: Optional[RoutingDecision] = None
