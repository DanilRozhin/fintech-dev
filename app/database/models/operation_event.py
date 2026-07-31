import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.enums import EventType, StatusType

if TYPE_CHECKING:
    from app.database.models.operation import OperationOrm
    from app.database.models.receipt_record import ReceiptRecordOrm


class OperationEventOrm(Base):
    __tablename__ = "operation_event"

    eventId: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    operationId: Mapped[str] = mapped_column(
        String(255),
        ForeignKey(
            column="operation.operationId",
            name="operation_event_operation_id_fk",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    type: Mapped[EventType] = mapped_column(
        Enum(
            EventType,
            name="operation_event_type_enum",
            check_constraint=True,
        ),
        nullable=False,
    )
    fromStatus: Mapped[StatusType | None] = mapped_column(
        Enum(
            StatusType,
            name="operation_event_from_status_enum",
            check_constraint=True,
        ),
        nullable=True,
    )
    toStatus: Mapped[StatusType] = mapped_column(
        Enum(
            StatusType,
            name="operation_event_to_status_enum",
            check_constraint=True,
        ),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    occurredAt: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    operation: Mapped["OperationOrm"] = relationship(
        back_populates="events",
    )
    receiptRecord: Mapped["ReceiptRecordOrm"] = relationship(
        back_populates="event",
    )
