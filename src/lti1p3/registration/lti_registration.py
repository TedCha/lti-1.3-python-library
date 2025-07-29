from dataclasses import dataclass

from lti1p3.lti_platform import LtiPlatform
from lti1p3.lti_tool import LtiTool


@dataclass(frozen=True)
class LtiRegistration:
    """
    See: http://www.imsglobal.org/spec/lti/v1p3/#tool-deployment-0
    """
    identifier: str
    client_id: str
    platform: LtiPlatform
    tool: LtiTool
    deployment_ids: list[str]
    tool_key_set: ...
    platform_jwks_url: str

    def has_deployment_id(self, value: str):
        return value in self.deployment_ids

    def get_default_deployment_id(self) -> str:
        return self.deployment_ids[0]