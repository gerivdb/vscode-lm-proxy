"""
Automatically extracted BatchQueryRequest class
"""


class BatchQueryRequest(BaseModel):
    prompts: List[str] = Field(..., description="List of prompts to process")
    task_metadata: Optional[TaskMetadata] = Field(
        None, description="Task context for routing"
    )
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional options"
    )
