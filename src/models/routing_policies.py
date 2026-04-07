"""
Routing Policies Management for LLM Task Router
"""

from typing import Any, Dict


class RoutingPolicies:
    """
    Encapsulates logic for managing routing policies.
    """

    def __init__(self):
        super().__init__()
        self.routing_policies = self._initialize_default_policies()

    def _initialize_default_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize default routing policies for different task types - VS Code LM API official models only"""
        return {
            "code_analysis": {
                "model_priorities": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "o1",
                    "o1-mini",
                    "claude-3.5-sonnet",
                ],
                "required_capabilities": ["code_analysis", "reasoning"],
                "cost_weight": 0.2,
                "performance_weight": 0.5,
                "latency_weight": 0.3,
            },
            "code_generation": {
                "model_priorities": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "o1",
                    "o1-mini",
                    "claude-3.5-sonnet",
                ],
                "required_capabilities": ["code_generation", "coding"],
                "cost_weight": 0.3,
                "performance_weight": 0.4,
                "latency_weight": 0.3,
            },
            "debugging": {
                "model_priorities": [
                    "gpt-4o",
                    "o1",
                    "gpt-4o-mini",
                    "o1-mini",
                    "claude-3.5-sonnet",
                ],
                "required_capabilities": ["debugging", "reasoning", "code_analysis"],
                "cost_weight": 0.2,
                "performance_weight": 0.5,
                "latency_weight": 0.3,
            },
            "testing": {
                "model_priorities": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "o1",
                    "o1-mini",
                    "claude-3.5-sonnet",
                ],
                "required_capabilities": ["testing", "code_generation"],
                "cost_weight": 0.4,
                "performance_weight": 0.3,
                "latency_weight": 0.3,
            },
            "documentation": {
                "model_priorities": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "o1",
                    "o1-mini",
                    "claude-3.5-sonnet",
                ],
                "required_capabilities": ["documentation", "writing"],
                "cost_weight": 0.3,
                "performance_weight": 0.4,
                "latency_weight": 0.3,
            },
            "refactoring": {
                "model_priorities": [
                    "gpt-4o",
                    "o1",
                    "gpt-4o-mini",
                    "o1-mini",
                    "claude-3.5-sonnet",
                ],
                "required_capabilities": ["refactoring", "code_generation"],
                "cost_weight": 0.3,
                "performance_weight": 0.4,
                "latency_weight": 0.3,
            },
            "optimization": {
                "model_priorities": [
                    "o1",
                    "gpt-4o",
                    "o1-mini",
                    "gpt-4o-mini",
                    "claude-3.5-sonnet",
                ],
                "required_capabilities": ["optimization", "reasoning"],
                "cost_weight": 0.2,
                "performance_weight": 0.5,
                "latency_weight": 0.3,
            },
            "translation": {
                "model_priorities": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "o1",
                    "o1-mini",
                    "claude-3.5-sonnet",
                ],
                "required_capabilities": ["translation", "language"],
                "cost_weight": 0.5,
                "performance_weight": 0.3,
                "latency_weight": 0.2,
            },
            "general": {
                "model_priorities": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "o1",
                    "o1-mini",
                    "claude-3.5-sonnet",
                ],
                "required_capabilities": [],
                "cost_weight": 0.4,
                "performance_weight": 0.3,
                "latency_weight": 0.3,
            },
        }

    def get_routing_policies(self) -> Dict[str, Any]:
        """Get current routing policies."""
        return self.routing_policies

    def update_routing_policies(self, policies: Dict[str, Any]) -> bool:
        """Update routing policies."""
        try:
            self.routing_policies.update(policies)
            return True
        except Exception:
            return False
