from typing import Protocol

from lti1p3.lti_deployment import LtiDeployment
from lti1p3.lti_registration import LtiRegistration


class Database(Protocol):
    def find_registration_by_issuer(self, iss: str, client_id: str = "") -> LtiRegistration:
        ...

    def find_deployment(self, iss: str, deployment_id: str, client_id: str = "") -> LtiDeployment:
        ...
