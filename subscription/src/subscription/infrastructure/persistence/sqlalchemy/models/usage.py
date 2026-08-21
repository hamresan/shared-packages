from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from subscription.infrastructure.persistence.sqlalchemy.base import SubscriptionBase


class UsageRecordModel(SubscriptionBase):
    __tablename__ = "subscription_usage_record"
    __table_args__ = (
        Index(
            "ix_subscription_usage_subject_metric_time",
            "subject_type",
            "subject_id",
            "metric",
            "occurred_at",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_type: Mapped[str] = mapped_column(String(80))
    subject_id: Mapped[str] = mapped_column(String(255))
    metric: Mapped[str] = mapped_column(String(120))
    amount: Mapped[int] = mapped_column(Integer)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
