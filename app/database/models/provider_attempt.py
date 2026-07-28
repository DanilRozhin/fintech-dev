import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.enums import AttemptOutcomeType, TriggerType

if TYPE_CHECKING:
    from app.database.models.operation import OperationOrm


class ProviderAttemptOrm(Base):
    __tablename__ = "provider_attempt"

    providerAttemptId: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    operationId: Mapped[str] = mapped_column(
        String(255),
        ForeignKey(
            column="operation.operationId",
            name="provider_attempt_operation_id_fk",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    attemptNumber: Mapped[int] = mapped_column(
        nullable=False,
    )
    requestedAt: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    triggeredBy: Mapped[TriggerType] = mapped_column(
        Enum(
            TriggerType,
            name="provider_attempt_triggered_by_enum",
            check_constraint=True,
        ),
        nullable=False,
    )
    outcome: Mapped[AttemptOutcomeType] = mapped_column(
        Enum(
            AttemptOutcomeType,
            name="provider_attempt_outcome_enum",
            check_constraint=True,
        ),
        nullable=False,
    )
    httpStatusCode: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    operation: Mapped["OperationOrm"] = relationship(
        back_populates="providerAttempts",
    )
