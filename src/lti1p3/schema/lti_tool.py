from dataclasses import dataclass


@dataclass(frozen=True)
class LtiTool:
    identifier: str
    name: str
    initiate_login_url: str
    redirect_uris: str
    client_name: str
    jwks_uri: str
    logo_uri: str
    domain: str
    description: str
    target_link_uri: str
    custom_parameters: str
    use_deep_linking: bool
