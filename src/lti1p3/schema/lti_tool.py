from dataclasses import dataclass


@dataclass(frozen=True)
class LtiTool:
    identifier: str
    name: str
    issuer: str
    oidc_initiation_url: str
    launch_url: str
    deep_linking_url: str
    jwks_url: str
