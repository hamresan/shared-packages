"""Meta Instagram authorization configuration."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaInstagramOAuthConfig:
    """Provider configuration supplied by the host composition root."""

    client_id: str
    client_secret: str
    graph_api_version: str
    token_endpoint: str = "https://api.instagram.com/oauth/access_token"
    graph_base_url: str = "https://graph.instagram.com"
