from pydantic import BaseModel, Field, field_validator


class ExecutionOutput(BaseModel):
    content: str = Field(
        description="Final executed content for the current step"
    )
    word_count: int = Field(
        description="Number of words in content"
    )

    @field_validator("word_count")
    def validate_word_count(cls, v):
        if v <= 0:
            raise ValueError("Word count must be positive")
        return v

    @field_validator("content")
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v
