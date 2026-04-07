"""
Automatically extracted RoutingPolicy class
"""


class RoutingPolicy(BaseModel):
    task_type: str
    model_priorities: List[str]
    cost_weight: float = 0.3
    performance_weight: float = 0.4
    latency_weight: float = 0.3
