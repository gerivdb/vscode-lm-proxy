"""
Automatically extracted AgentResult class
"""


class AgentResult:
    """Result from an agent execution"""

    task_id: str
    agent_id: str
    content: str
    model_used: str
    tokens_used: int
    latency_ms: int
    cost: Optional[float] = None
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
