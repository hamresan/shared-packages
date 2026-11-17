from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from customer.application.factories import CustomerFactory
from customer.domain import CustomerErasedError, CustomerInvalidStateError, CustomerStatus


def test_customer_lifecycle_and_version_are_deterministic() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    customer = CustomerFactory().create(uuid4(), uuid4(), None, now)
    assert customer.version == 1
    assert customer.status is CustomerStatus.ACTIVE
    assert customer.created_at == customer.updated_at == now

    later = now + timedelta(days=1)
    customer.update_profile("Ada", later)
    assert (customer.display_name, customer.version, customer.updated_at) == ("Ada", 2, later)
    customer.archive(later)
    assert customer.status is CustomerStatus.ARCHIVED
    assert customer.archived_at == later
    assert customer.version == 3
    with pytest.raises(CustomerInvalidStateError):
        customer.archive(later)
    with pytest.raises(CustomerInvalidStateError):
        customer.update_profile("Other", later)

    customer.reactivate(later)
    assert customer.status is CustomerStatus.ACTIVE
    assert customer.archived_at is None
    assert customer.version == 4
    with pytest.raises(CustomerInvalidStateError):
        customer.reactivate(later)


def test_erasure_is_terminal() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    customer = CustomerFactory().create(uuid4(), uuid4(), "Ada", now)
    customer.status = CustomerStatus.ERASED
    with pytest.raises(CustomerErasedError):
        customer.archive(now)
    with pytest.raises(CustomerErasedError):
        customer.reactivate(now)
    with pytest.raises(CustomerErasedError):
        customer.update_profile("Other", now)
