import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.database.enums import AttemptOutcomeType, TriggerType


class AttemptSingle(BaseModel):
    providerAttemptId: int = Field(description="Attempt ID, unique")
    operationId: str = Field(description="ID of the operation the attempt related with")
    attemptNumber: int = Field(description="Attempt number")
    requestedAt: datetime.datetime = Field(description="Time when the request was made")
    triggeredBy: TriggerType = Field(description="Why the attempt was made")
    outcome: AttemptOutcomeType = Field(description="Result of the attempt")
    httpStatusCode: int | None = Field(description="Status code of the http response")

    model_config = ConfigDict(from_attributes=True)
