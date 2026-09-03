from instagram_auth.baseline import InstagramConnectionState, InstagramProviderErrorKind


def test_connection_state_values_are_stable() -> None:
    assert {state.value for state in InstagramConnectionState} == {
        "authorizing",
        "connected",
        "reauthorization_required",
        "disconnected",
    }


def test_provider_error_kinds_are_provider_independent() -> None:
    assert InstagramProviderErrorKind.INVALID_AUTHORIZATION_CODE.value == "invalid_authorization_code"
    assert InstagramProviderErrorKind.INSUFFICIENT_PERMISSIONS.value == "insufficient_permissions"
    assert InstagramProviderErrorKind.PROVIDER_UNAVAILABLE.value == "provider_unavailable"
