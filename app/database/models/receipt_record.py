import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.enums import ReceiptResultType

if TYPE_CHECKING:
    from app.database.models.operation import OperationOrm
    from app.database.models.operation_event import OperationEventOrm


class ReceiptRecordOrm(Base):
    __tablename__ = "receipt_record"

    receiptRecordId: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    operationId: Mapped[str] = mapped_column(
        String(255),
        ForeignKey(
            column="operation.operationId",
            name="receipt_record_operation_id_fk",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    providerPaymentId: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    result: Mapped[ReceiptResultType] = mapped_column(
        Enum(
            ReceiptResultType,
            name="receipt_record_result_enum",
            check_constraint=True,
        ),
        nullable=False,
    )
    providerMessage: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    occurredAtProvider: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    receivedAt: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    eventId: Mapped[int] = mapped_column(
        ForeignKey(
            column="operation_event.eventId",
            name="receipt_record_event_id_fk",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    operation: Mapped["OperationOrm"] = relationship(
        back_populates="receiptRecords",
    )
    event: Mapped["OperationEventOrm"] = relationship(
        back_populates="receiptRecord",
    )
