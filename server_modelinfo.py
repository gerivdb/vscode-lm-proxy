"""
Automatically extracted ModelInfo class
"""


class ModelInfo(BaseModel):
    name: str
    provider: str
    context_size: int
    capabilities: List[str]
    latency_ms: Optional[float] = None
    tokens_per_sec: Optional[float] = None
    cost_per_token: Optional[float] = None
