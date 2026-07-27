from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    message: str = Field(description="Message in health endpoint")
    status: str = Field(description="Status in health endpoint")
