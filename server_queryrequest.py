"""
Automatically extracted QueryRequest class
"""


class QueryRequest(BaseModel):
    prompt: str = Field(..., description="The query prompt")
    model: Optional[str] = Field(None, description="Specific model to use")
    task_metadata: Optional[TaskMetadata] = Field(
        None, description="Task context for routing"
    )
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional options"
    )
