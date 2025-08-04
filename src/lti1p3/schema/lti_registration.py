from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LtiRegistration:
    """
    See: https://www.imsglobal.org/spec/lti/v1p3/#tool-deployment-0
    """
    identifier: str
    client_id: str
    issuer: str
    audience: str
    authentication_url: str
    access_token_url: str
    jwks_url: str
    is_active: str
    tool_id: str


class LtiRegistrationRepository(Protocol):
    def find(self, identifier: str) -> LtiRegistration | None:
        ...

    def find_by_client_id(self, client_id: str) -> list[LtiRegistration] | None:
        ...

    def find_by_platform_issuer(self, issuer: str, client_id: str) -> LtiRegistration | None:
        ...

    def find_by_tool_issuer(self, issuer: str, client_id: str) -> LtiRegistration | None:
        ...
