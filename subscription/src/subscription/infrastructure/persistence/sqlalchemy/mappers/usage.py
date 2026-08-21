from subscription.domain import SubjectReference, UsageMetric, UsageRecord
from subscription.infrastructure.persistence.sqlalchemy.models import UsageRecordModel


class UsagePersistenceMapper:
    def to_model(self, record: UsageRecord) -> UsageRecordModel:
        return UsageRecordModel(
            subject_type=record.subject.subject_type,
            subject_id=record.subject.subject_id,
            metric=record.metric.key,
            amount=record.amount,
            occurred_at=record.occurred_at,
        )

    def to_domain(self, model: UsageRecordModel) -> UsageRecord:
        return UsageRecord(
            subject=SubjectReference(model.subject_type, model.subject_id),
            metric=UsageMetric(model.metric),
            amount=model.amount,
            occurred_at=model.occurred_at,
        )
