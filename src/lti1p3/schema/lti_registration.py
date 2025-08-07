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


class FindLtiRegistrationByPlatformIssuer(Protocol):
    def __call__(self, issuer: str, client_id: str) -> LtiRegistration | None:
        ...


class FindLtiRegistration(Protocol):
    def __call__(self, identifier: str) -> LtiRegistration | None:
        ...
