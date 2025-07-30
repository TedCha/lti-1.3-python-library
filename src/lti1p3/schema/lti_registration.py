from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LtiRegistration:
    """
    See: http://www.imsglobal.org/spec/lti/v1p3/#tool-deployment-0
    """
    identifier: str
    client_id: str
    platform_audience: str
    platform_authentication_url: str
    platform_access_token_url: str
    platform_jwks_url: str
    is_active: str
    tool_public_key: str | None
    tool_private_key: str | None
    deployment_ids: list[str]

    def has_deployment_id(self, value: str):
        return value in self.deployment_ids


class LtiRegistrationRepository(Protocol):
    def find(self, identifier: str) -> LtiRegistration | None:
        ...

    def find_by_client_id(self, client_id: str) -> list[LtiRegistration] | None:
        ...

    def find_by_platform_issuer(self, issuer: str, client_id: str) -> LtiRegistration | None:
        ...

    def find_by_tool_issuer(self, issuer: str, client_id: str) -> LtiRegistration | None:
        ...
