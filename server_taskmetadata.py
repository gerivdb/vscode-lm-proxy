"""
Automatically extracted TaskMetadata class
"""


class TaskMetadata(BaseModel):
    task_type: str = Field(
        ..., description="Type of task (code_analysis, code_generation, etc.)"
    )
    complexity: str = Field(
        ..., description="Task complexity (simple, medium, complex)"
    )
    context_size: int = Field(..., description="Required context window size")
    latency_budget: Optional[int] = Field(
        None, description="Maximum acceptable latency in ms"
    )
    priority: str = Field(
        "normal", description="Task priority (low, normal, high, critical)"
    )
