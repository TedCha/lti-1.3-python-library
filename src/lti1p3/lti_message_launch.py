from lti1p3.exception import LtiException, LtiExceptionType
from lti1p3.key_value_repository import KeyValueRepository
from lti1p3.registration.lti_registration_repository import LtiRegistrationRepository


class LtiMessageLaunch:
    def __init__(
            self,
            registration_repository: LtiRegistrationRepository,
            key_value_repository: KeyValueRepository
    ):
        self._registration_repository = registration_repository
        self._key_value_repository = key_value_repository

    def launch(self):
        ...

    def validate_platform_originating_launch_request(self, request: dict):
        """
        Validates the launch request.

        Raises:
            LtiException
        """
        if "state" not in request:
            raise LtiException(LtiExceptionType.MISSING_STATE, message="missing state")

        if "id_token" not in request:
            raise LtiException(LtiExceptionType.MISSING_ID_TOKEN, message="missing id_token")

    def validate_state(self, request: dict):
        """
        Validates OIDC state parameter.

        Raises:
            LtiException
        """
        received_state = request["state"]
        retrieved_state = self._key_value_repository.get("lti1p3-state")

        if received_state != retrieved_state:
            raise LtiException(LtiExceptionType.INVALID_STATE, message="invalid state parameter")

        # TODO: Need to figure out how to get the registration properly. One way is to decode
        #  the id_token without verifying the signature, but I wonder if there's another way?