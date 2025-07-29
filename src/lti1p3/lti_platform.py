from dataclasses import dataclass


@dataclass(frozen=True)
class LtiPlatform:
    identifier: str
    name: str
    audience: str
    oidc_authentication_url: str
    oauth2_access_token_url: str