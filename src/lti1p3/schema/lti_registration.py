from dataclasses import dataclass
from typing import Protocol

from lti1p3.schema.lti_platform import LtiPlatform
from lti1p3.schema.lti_tool import LtiTool


@dataclass(frozen=True)
class LtiRegistration:
    """
    See: http://www.imsglobal.org/spec/lti/v1p3/#tool-deployment-0
    """
    identifier: str
    client_id: str
    deployment_ids: list[str]
    platform: LtiPlatform
    tool: LtiTool
    kid: str

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
