"""
Automatically extracted AgentConfig class
"""


class AgentConfig:
    """Configuration for an agent"""

    agent_id: str
    role: str
    expertise: List[str] = field(default_factory=list)
    model_preference: Optional[str] = None
    max_iterations: int = 3
    temperature: float = 0.7
