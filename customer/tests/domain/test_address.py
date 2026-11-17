from uuid import uuid4

from customer.domain.address import CustomerAddress


def test_address_updates_preserve_identity_and_explicit_default() -> None:
    address = CustomerAddress(
        uuid4(), uuid4(), uuid4(), "Old", "OM", "Original", "Muscat", None, None, False
    )
    original_id, original_business = address.id, address.business_id

    address.change_details("Office", "OM", "New street", "Seeb", "Muscat", "100")
    address.make_default()

    assert address.id == original_id and address.business_id == original_business
    assert (address.label, address.line1, address.city, address.region, address.postal_code) == (
        "Office",
        "New street",
        "Seeb",
        "Muscat",
        "100",
    )
    assert address.is_default is True
