from identity.infrastructure.persistence.sqlalchemy import IdentityBase
from identity.infrastructure.persistence.sqlalchemy.models import OtpChallengeModel


def test_all_identity_tables_use_identity_prefix() -> None:
    table_names = set(IdentityBase.metadata.tables)

    assert table_names == {
        "identity_users",
        "identity_user_identities",
        "identity_otp_challenges",
        "identity_sessions",
    }
    assert all(name.startswith("identity_") for name in table_names)


def test_otp_challenges_define_hot_query_composite_index() -> None:
    indexes = {index.name: index for index in OtpChallengeModel.__table__.indexes}
    index = indexes["ix_identity_otp_challenges_destination_purpose_created_at"]

    assert [column.name for column in index.columns] == [
        "normalized_destination",
        "purpose",
        "created_at",
    ]
