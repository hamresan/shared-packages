from instagram_auth.baseline import InstagramAccountType
from instagram_auth.domain import InstagramExternalIdentity


def test_external_identity_preserves_opaque_provider_identifier() -> None:
    identity = InstagramExternalIdentity(
        provider_user_id="ig-account:001/opaque",
        username="shop_creator",
        account_type=InstagramAccountType.CREATOR,
    )

    assert identity.provider == "instagram"
    assert identity.provider_user_id == "ig-account:001/opaque"
    assert identity.account_type is InstagramAccountType.CREATOR
