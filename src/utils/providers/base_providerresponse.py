"""
Automatically extracted ProviderResponse class
"""


class ProviderResponse:
    """Standardized response from any provider"""

    content: str
    model_used: str
    tokens_used: int
    latency_ms: int
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
