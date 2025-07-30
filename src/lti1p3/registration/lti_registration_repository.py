from typing import Protocol

from lti1p3.registration.lti_registration import LtiRegistration


class LtiRegistrationRepository(Protocol):
    def find(self, identifier: str) -> LtiRegistration | None:
        ...

    def find_all(self, identifier: str) -> list[LtiRegistration]:
        ...

    def find_by_client_id(self, client_id: str) -> LtiRegistration | None:
        ...

    def find_by_platform_issuer(self, issuer: str, client_id: str = None) -> LtiRegistration | None:
        ...

    # TODO: Only supporting tool acting use cases at this time
    # def find_by_tool_issuer(self, issuer: str, client_id: str) -> LtiRegistration | None:
    #     ...
