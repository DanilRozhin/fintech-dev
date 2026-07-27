import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.database.enums import StatusType


class OperationBase(BaseModel):
    operationId: str = Field(description="Operation ID, unique")
    amount: str = Field(description="Amount of operation")
    currency: str = Field(description="Currency of operation")
    description: str = Field(description="Operation description")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("amount", mode="after")
    @classmethod
    def validate_amount(cls, v: str) -> str:
        try:
            amount = Decimal(v)
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            if amount.as_tuple().exponent < -2:
                raise ValueError("Maximum 2 digits after decimal point")
            return v
        except Exception:
            raise ValueError("Invalid amount format") from None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v):
        if v != "RUB":
            raise ValueError("Currency must be RUB")
        return v


class OperationRequest(OperationBase):
    pass


class OperationResponse(OperationBase):
    status: StatusType = Field(description="Operation status")
    providerPaymentId: uuid.UUID = Field(description="Provider payment ID")
    created_at: datetime.datetime = Field(description="Time the record was created")
    updated_at: datetime.datetime = Field(description="Time the record was lastly updated")
