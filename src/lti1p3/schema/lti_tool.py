from dataclasses import dataclass


@dataclass(frozen=True)
class LtiTool:
    identifier: str
    name: str
    description: str
    url: str
    initiate_login_url: str
    redirect_uris: list[str]
    jwks_uri: str
    logo_uri: str
    target_link_uri: str
    custom_parameters: dict
    use_deep_linking: bool
