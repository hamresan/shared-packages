import integration_auth


def test_package_exposes_stage_one_domain_api() -> None:
    assert set(integration_auth.__all__) == {
        "CredentialDirection",
        "CredentialLifecyclePolicy",
        "CredentialStatus",
        "IntegrationClient",
        "IntegrationClientId",
        "IntegrationCredential",
        "IntegrationCredentialId",
        "IntegrationPrincipal",
        "IntegrationResource",
        "IntegrationScope",
        "Permission",
    }
