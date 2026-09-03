from instagram_auth.application.contracts import InstagramAccessTokenProtector


class PrefixTokenProtector(InstagramAccessTokenProtector):
    """Deterministic credential protector fake for persistence tests."""

    def protect(self, access_token: str) -> str:
        return f"protected::{access_token[::-1]}"

    def unprotect(self, protected_access_token: str) -> str:
        prefix = "protected::"
        if not protected_access_token.startswith(prefix):
            raise ValueError("Unexpected protected token format")
        return protected_access_token.removeprefix(prefix)[::-1]
