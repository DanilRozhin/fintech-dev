import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.database.enums import ReceiptResultType


class ReceiptSingle(BaseModel):
    receiptRecordId: int = Field(description="Receipt Record ID, unique")
    operationId: str = Field(description="ID of the operation the record related with")
    providerPaymentId: uuid.UUID = Field(description="Provider payment ID")
    result: ReceiptResultType = Field(description="Result, completed or rejected")
    providerMessage: str = Field(description="Provider message")
    occurredAtProvider: datetime.datetime = Field(description="Action time, given by provider")
    receivedAt: datetime.datetime = Field(description="Time the record was created")
    eventId: int = Field(description="ID of the event the record related with")

    model_config = ConfigDict(from_attributes=True)
