import datetime
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.enums import CurrencyType, StatusType

if TYPE_CHECKING:
    from app.database.models.operation_event import OperationEventOrm
    from app.database.models.provider_attempt import ProviderAttemptOrm
    from app.database.models.receipt_record import ReceiptRecordOrm


class OperationOrm(Base):
    __tablename__ = "operation"

    operationId: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False,
    )
    currency: Mapped[CurrencyType] = mapped_column(
        Enum(
            CurrencyType,
            name="operation_currency_enum",
            check_constraint=True,
        ),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    status: Mapped[StatusType] = mapped_column(
        Enum(
            StatusType,
            name="operation_status_enum",
            check_constraint=True,
        ),
        nullable=False,
        server_default=StatusType.CREATED.value,
    )
    providerPaymentId: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        unique=True,
    )
    createdAt: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updatedAt: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    events: Mapped[list["OperationEventOrm"]] = relationship(
        back_populates="operation",
    )
    receiptRecords: Mapped[list["ReceiptRecordOrm"]] = relationship(
        back_populates="operation",
    )
    providerAttempts: Mapped[list["ProviderAttemptOrm"]] = relationship(
        back_populates="operation",
    )
