from datetime import UTC, datetime
from uuid import uuid4

from customer.domain.contact import ContactKind, CustomerContact


def test_changing_contact_value_revokes_prior_verification() -> None:
    now = datetime.now(UTC)
    contact = CustomerContact(
        uuid4(),
        uuid4(),
        uuid4(),
        ContactKind.EMAIL,
        "old@example.com",
        False,
        now,
        verified_at=now,
        verification_method="trusted_provider",
    )

    contact.change_value("new@example.com")
    assert contact.value == "new@example.com"
    assert contact.verified_at is None
    assert contact.verification_method is None

    contact.make_primary()
    assert contact.is_primary is True
