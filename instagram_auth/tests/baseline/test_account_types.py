from instagram_auth.baseline import InstagramAccountType, is_eligible_account_type


def test_business_account_is_eligible() -> None:
    assert is_eligible_account_type(InstagramAccountType.BUSINESS)


def test_creator_account_is_eligible() -> None:
    assert is_eligible_account_type(InstagramAccountType.CREATOR)


def test_consumer_account_is_not_eligible() -> None:
    assert not is_eligible_account_type("consumer")


def test_unknown_account_type_is_not_eligible() -> None:
    assert not is_eligible_account_type("unknown")
