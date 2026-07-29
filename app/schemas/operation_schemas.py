import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.database.enums import CurrencyType, StatusType


class OperationCreate(BaseModel):
    operationId: str = Field(description="Operation ID, unique")
    amount: Decimal = Field(description="Amount of operation")
    currency: CurrencyType = Field(description="Currency of operation")
    description: str | None = Field(description="Operation description")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("amount", mode="after")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Amount must be positive")
        exponent = value.as_tuple().exponent
        if isinstance(exponent, int) and exponent < -2:
            raise ValueError("Amount must have at most 2 decimal places")
        return value


class OperationSingleResponse(BaseModel):
    operationId: str = Field(description="Operation ID, unique")
    amount: Decimal = Field(description="Amount of operation")
    currency: CurrencyType = Field(description="Currency of operation")
    description: str | None = Field(description="Operation description")
    status: StatusType = Field(description="Operation status")
    providerPaymentId: uuid.UUID | None = Field(description="Provider payment ID")
    createdAt: datetime.datetime = Field(description="Time the record was created")
    updatedAt: datetime.datetime = Field(description="Time the record was lastly updated")

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> str:
        return str(value)


class OperationSubmitResponse(BaseModel):
    operation: OperationSingleResponse | None = Field(description="Operation details")
    is_submitted: bool = Field(description="Whether the operation was submitted or not")

    model_config = ConfigDict(from_attributes=True)
