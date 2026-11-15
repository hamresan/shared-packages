from uuid import uuid4

import pytest

from tests.support.http_environment import HttpEnvironment

OWNER = {"Authorization": "Bearer owner-token"}
MEMBER = {"Authorization": "Bearer member-token"}


@pytest.mark.asyncio
async def test_authentication_and_business_isolation(
    business_http_environment: HttpEnvironment,
) -> None:
    client = business_http_environment.client
    payload = {
        "name": "Muscat Cafe",
        "country_code": "OM",
        "default_language": "en",
        "default_currency_code": "OMR",
    }
    assert (await client.post("/businesses", json=payload)).status_code == 401
    assert (
        await client.post("/businesses", json=payload, headers={"Authorization": "Bearer forged"})
    ).status_code == 401
    created = await client.post("/businesses", json=payload, headers=OWNER)
    assert created.status_code == 201, created.text
    business_id = created.json()["id"]
    assert (await client.get("/businesses", headers=OWNER)).json()[0]["id"] == business_id
    assert (await client.get("/businesses", headers=MEMBER)).json() == []
    assert (await client.get(f"/businesses/{business_id}", headers=MEMBER)).status_code == 404
    assert (
        await client.put(f"/businesses/{business_id}", headers=MEMBER, json={"name": "Stolen"})
    ).status_code == 404
    assert (await client.get(f"/businesses/{business_id}/branches", headers=OWNER)).json() == []
    assert (
        await client.post(
            "/businesses", headers=OWNER, json={**payload, "default_currency_code": "INVALID"}
        )
    ).status_code == 422


@pytest.mark.asyncio
async def test_member_invitation_and_role_authorization(
    business_http_environment: HttpEnvironment,
) -> None:
    client = business_http_environment.client
    created = await client.post(
        "/businesses",
        headers=OWNER,
        json={
            "name": "Store",
            "country_code": "OM",
            "default_language": "en",
            "default_currency_code": "OMR",
        },
    )
    business_id = created.json()["id"]
    invited = await client.post(
        f"/businesses/{business_id}/memberships",
        headers=OWNER,
        json={"user_id": str(business_http_environment.other_id)},
    )
    assert invited.status_code == 201, invited.text
    membership_id = invited.json()["id"]
    assert invited.json()["branch_access_scope"] == "selected"
    assert (await client.get(f"/businesses/{business_id}", headers=MEMBER)).status_code == 404
    assert (
        await client.post(f"/businesses/{business_id}/memberships/accept", headers=MEMBER)
    ).status_code == 200
    assert (await client.get(f"/businesses/{business_id}", headers=MEMBER)).status_code == 200
    assert (
        await client.get(f"/businesses/{business_id}/memberships", headers=MEMBER)
    ).status_code == 403
    assert (
        await client.post(
            f"/businesses/{business_id}/memberships", headers=MEMBER, json={"user_id": str(uuid4())}
        )
    ).status_code == 403

    promoted = await client.put(
        f"/businesses/{business_id}/memberships/{membership_id}/role",
        headers=OWNER,
        json={"role": "manager"},
    )
    assert promoted.status_code == 200 and promoted.json()["branch_access_scope"] == "all"
    assert (
        await client.put(
            f"/businesses/{business_id}/memberships/{membership_id}/role",
            headers=OWNER,
            json={"role": "owner"},
        )
    ).status_code == 409
    assert (
        await client.put(
            f"/businesses/{business_id}/memberships/{membership_id}/access",
            headers=OWNER,
            json={"scope": "selected", "branch_ids": []},
        )
    ).status_code == 409
    assert (
        await client.get(f"/businesses/{business_id}/memberships", headers=OWNER)
    ).status_code == 200


@pytest.mark.asyncio
async def test_manager_branch_lifecycle_and_ownership_transfer(
    business_http_environment: HttpEnvironment,
) -> None:
    client = business_http_environment.client
    created = await client.post(
        "/businesses",
        headers=OWNER,
        json={
            "name": "Bakery",
            "country_code": "OM",
            "default_language": "en",
            "default_currency_code": "OMR",
        },
    )
    business_id = created.json()["id"]
    invited = await client.post(
        f"/businesses/{business_id}/memberships",
        headers=OWNER,
        json={"user_id": str(business_http_environment.other_id)},
    )
    membership_id = invited.json()["id"]
    await client.post(f"/businesses/{business_id}/memberships/accept", headers=MEMBER)
    await client.put(
        f"/businesses/{business_id}/memberships/{membership_id}/role",
        headers=OWNER,
        json={"role": "manager"},
    )
    branch = await client.post(
        f"/businesses/{business_id}/branches",
        headers=MEMBER,
        json={
            "name": "Main",
            "timezone": "Asia/Muscat",
            "address": {"city": "Muscat", "country_code": "OM"},
        },
    )
    assert branch.status_code == 201, branch.text
    branch_id = branch.json()["id"]
    assert (
        len(
            (
                await client.get(f"/businesses/{business_id}/branches?city=muscat", headers=MEMBER)
            ).json()
        )
        == 1
    )
    assert (
        await client.put(
            f"/businesses/{business_id}/branches/{branch_id}",
            headers=MEMBER,
            json={"name": "Updated", "timezone": "Asia/Muscat"},
        )
    ).status_code == 200
    assert (
        await client.delete(f"/businesses/{business_id}/branches/{branch_id}", headers=MEMBER)
    ).status_code == 200
    assert (
        await client.post(
            f"/businesses/{business_id}/branches/{branch_id}/reactivate", headers=MEMBER
        )
    ).status_code == 200
    transferred = await client.post(
        f"/businesses/{business_id}/ownership/transfer",
        headers=OWNER,
        json={"recipient_membership_id": membership_id},
    )
    assert transferred.status_code == 200 and transferred.json()["role"] == "owner"
    assert (await client.delete(f"/businesses/{business_id}", headers=OWNER)).status_code == 403
    assert (await client.delete(f"/businesses/{business_id}", headers=MEMBER)).status_code == 200


@pytest.mark.asyncio
async def test_revoked_member_and_cross_business_requests_are_hidden(
    business_http_environment: HttpEnvironment,
) -> None:
    client = business_http_environment.client
    payload = {
        "name": "Company",
        "country_code": "OM",
        "default_language": "en",
        "default_currency_code": "OMR",
    }
    first = (await client.post("/businesses", headers=OWNER, json=payload)).json()["id"]
    second = (
        await client.post("/businesses", headers=OWNER, json={**payload, "name": "Other"})
    ).json()["id"]
    invited = await client.post(
        f"/businesses/{first}/memberships",
        headers=OWNER,
        json={"user_id": str(business_http_environment.other_id)},
    )
    member_id = invited.json()["id"]
    await client.post(f"/businesses/{first}/memberships/accept", headers=MEMBER)
    assert (await client.get(f"/businesses/{first}", headers=MEMBER)).status_code == 200
    assert (await client.get(f"/businesses/{second}", headers=MEMBER)).status_code == 404
    assert (
        await client.post(
            f"/businesses/{second}/branches",
            headers=MEMBER,
            json={"name": "Foreign", "timezone": "Asia/Muscat"},
        )
    ).status_code == 404
    assert (
        await client.delete(f"/businesses/{first}/memberships/{member_id}", headers=OWNER)
    ).status_code == 200
    assert (await client.get(f"/businesses/{first}", headers=MEMBER)).status_code == 404
    assert (await client.get("/businesses", headers=MEMBER)).json() == []
