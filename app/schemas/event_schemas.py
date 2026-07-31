import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.database.enums import EventType, StatusType


class OperationEventSingle(BaseModel):
    eventId: int = Field(description="Event ID")
    type: EventType = Field(description="Event type")
    fromStatus: StatusType | None = Field(description="Past status of the event")
    toStatus: StatusType = Field(description="Updated status of the event")
    message: str = Field(description="Event message, describing the event")
    occurredAt: datetime.datetime = Field(description="Time the event occurred at")

    model_config = ConfigDict(from_attributes=True)


class OperationEventResponse(BaseModel):
    events: list[OperationEventSingle]
