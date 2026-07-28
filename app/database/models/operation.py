import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.enums import StatusType
from app.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.database.models.operation_event import OperationEventOrm


class OperationOrm(Base, TimestampMixin):
    __tablename__ = "operation"

    operationId: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        nullable=False,
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

    events: Mapped[list["OperationEventOrm"]] = relationship(
        back_populates="operation",
    )
