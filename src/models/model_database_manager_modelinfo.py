"""
Automatically extracted ModelInfo class
"""


class ModelInfo:
    """Informations détaillées sur un modèle LLM"""

    id: str
    provider: str
    family: str
    context_window: int
    pricing: str
    capabilities: List[str]
    recommended_for: List[str]
    tool_support: List[str] = field(
        default_factory=list
    )  # Outils qui supportent ce modèle
