from pydantic import BaseModel, Field, field_validator


class ExecutionOutput(BaseModel):
    content: str = Field(
        description="Final executed content for the current step"
    )
  

    @field_validator("content")
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v
