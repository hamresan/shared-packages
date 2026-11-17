from customer import CustomerPermission


def test_sensitive_permissions_are_distinct_from_profile_read() -> None:
    assert CustomerPermission.NOTES_READ != CustomerPermission.READ
    assert CustomerPermission.ERASE != CustomerPermission.UPDATE
    assert CustomerPermission.IDENTITY_LINK.value == "customer.identity.link"
