import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.database.enums import AttemptOutcomeType


class ProviderCallResult(BaseModel):
    providerPaymentId: uuid.UUID | None = Field(description="Attempt ID, unique")
    outcome: AttemptOutcomeType = Field(description="Result of the attempt")
    httpStatusCode: int | None = Field(description="Status code of the http response")
    errorDetail: str | None = Field(description="Details of the error")

    model_config = ConfigDict(from_attributes=True)
