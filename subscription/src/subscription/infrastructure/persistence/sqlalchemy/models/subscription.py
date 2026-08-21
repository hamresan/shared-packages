from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from subscription.infrastructure.persistence.sqlalchemy.base import SubscriptionBase


class SubscriptionModel(SubscriptionBase):
    __tablename__ = "subscription_subscription"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    subject_type: Mapped[str] = mapped_column(String(80), index=True)
    subject_id: Mapped[str] = mapped_column(String(255), index=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("subscription_plan.id"), index=True)
    subscription_type: Mapped[str] = mapped_column(String(20), index=True)
    source: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TrialPolicyModel(SubscriptionBase):
    __tablename__ = "subscription_trial_policy"

    subscription_id: Mapped[str] = mapped_column(
        ForeignKey("subscription_subscription.id", ondelete="CASCADE"),
        primary_key=True,
    )
    completion_mode: Mapped[str] = mapped_column(String(20))
    max_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)


class TrialUsageConditionModel(SubscriptionBase):
    __tablename__ = "subscription_trial_usage_condition"
    __table_args__ = (
        UniqueConstraint(
            "subscription_id",
            "metric",
            "period",
            name="trial_usage_metric_period",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subscription_id: Mapped[str] = mapped_column(
        ForeignKey("subscription_subscription.id", ondelete="CASCADE"),
        index=True,
    )
    metric: Mapped[str] = mapped_column(String(120))
    period: Mapped[str] = mapped_column(String(30))
    limit: Mapped[int] = mapped_column(Integer)
