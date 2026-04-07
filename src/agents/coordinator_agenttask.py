"""
Automatically extracted AgentTask class
"""


class AgentTask:
    """A task assigned to an agent"""

    task_id: str
    agent_id: str
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    priority: int = 1
    timeout_seconds: int = 300
