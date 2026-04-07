"""
Automatically extracted SystemStatus class
"""


class SystemStatus(BaseModel):
    status: str
    uptime: float
    total_requests: int
    active_models: int
    version: str
    timestamp: datetime
