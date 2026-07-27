import uuid

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.enums import StatusType
from app.database.mixins import TimestampMixin


class OperationOrm(Base, TimestampMixin):
    __tablename__ = "operation"

    operationId: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )
    amount: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    status: Mapped[StatusType] = mapped_column(
        Enum(
            StatusType,
            name="operation_status_enum",
            check_constraint=True,
        ),
        nullable=False,
    )
    providerPaymentId: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
