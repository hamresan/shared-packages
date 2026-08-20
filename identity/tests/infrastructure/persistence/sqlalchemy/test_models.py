from typing import cast

from sqlalchemy import Index, Table

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
    table = cast(Table, OtpChallengeModel.__table__)
    index = next(
        cast(Index, candidate)
        for candidate in table.indexes
        if str(candidate.name) == "ix_identity_otp_challenges_destination_purpose_created_at"
    )

    assert [column.name for column in index.columns] == [
        "normalized_destination",
        "purpose",
        "created_at",
    ]
