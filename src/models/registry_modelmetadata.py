"""
Automatically extracted ModelMetadata class
"""


class ModelMetadata:
    """Metadata for an LLM model"""

    name: str
    provider: str
    context_size: int
    capabilities: List[str] = field(default_factory=list)
    latency_ms: Optional[float] = None
    tokens_per_sec: Optional[float] = None
    cost_per_token: Optional[float] = None
    api_endpoint: Optional[str] = None
    api_key_required: bool = True
    max_tokens_per_request: Optional[int] = None
    supported_parameters: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"  # active, inactive, deprecated
