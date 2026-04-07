"""
Automatically extracted LMHackResponse class
"""


class LMHackResponse(BaseModel):
    content: str
    model_used: str
    tokens_used: int
    latency_ms: int
    cost: Optional[float] = None
