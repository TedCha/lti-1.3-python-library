from dataclasses import dataclass


@dataclass(frozen=True)
class LtiTool:
    identifier: str
    name: str
    audience: str
    oidc_initiation_url: str
    launch_url: str
    deep_linking_url: str