from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from subscription.infrastructure.persistence.sqlalchemy.base import SubscriptionBase


class PlanModel(SubscriptionBase):
    __tablename__ = "subscription_plan"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    subscription_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), index=True)


class PlanEntitlementModel(SubscriptionBase):
    __tablename__ = "subscription_plan_entitlement"
    __table_args__ = (UniqueConstraint("plan_id", "key", name="plan_entitlement_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[str] = mapped_column(
        ForeignKey("subscription_plan.id", ondelete="CASCADE"),
        index=True,
    )
    key: Mapped[str] = mapped_column(String(120))
    value_type: Mapped[str] = mapped_column(String(20))
    boolean_value: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    integer_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    decimal_value: Mapped[Decimal | None] = mapped_column(Numeric(38, 12), nullable=True)
    string_value: Mapped[str | None] = mapped_column(Text, nullable=True)
