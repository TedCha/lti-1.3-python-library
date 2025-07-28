from lti1p3.exception import LtiException, LtiExceptionType
from lti1p3.helpers import create_secure_hash
from lti1p3.registration.lti_registration_repository import LtiRegistrationRepository


class LtiOidcLogin:
    def __init__(self, repository: LtiRegistrationRepository, ):
        self.repository = repository

    @staticmethod
    def validate_oidc_login_request(request: dict):
        """
        Validates the OIDC login request.

        Raises:
            LtiException
        """
        if "iss" not in request:
            raise LtiException(LtiExceptionType.MISSING_LOGIN_PARAMETERS, message="missing iss")

        if "login_hint" not in request:
            raise LtiException(LtiExceptionType.MISSING_LOGIN_PARAMETERS, message="missing login_hint")

        if "target_link_uri" not in request:
            raise LtiException(LtiExceptionType.MISSING_LOGIN_PARAMETERS, message="missing target_link_uri")

    def initiate(self, request: dict):
        """
        See: https://www.imsglobal.org/spec/security/v1p0/#openid_connect_launch_flow
        """
        self.validate_oidc_login_request(request)

        registration = self.repository.find_by_tool_issuer(request["iss"], request["client_id"])

        if not registration:
            raise LtiException(LtiExceptionType.NO_REGISTRATION, message="registration not found")

        tool_key_chain = registration.tool_key_chain

        if not tool_key_chain:
            raise LtiException(
                LtiExceptionType.NO_TOOL_KEY_CHAIN,
                message="registration does not have a configured tool key chain",
                identifier=registration.identifier
            )

        deployment_id = request["lti_deployment_id"]
        if deployment_id and not registration.has_deployment_id(deployment_id):
            raise LtiException(LtiExceptionType.NO_DEPLOYMENT, message="deployment not found for registration")

        auth_request = {
            "scope": "openid",
            "response_type": "id_token",
            "client_id": request["client_id"],
            "redirect_uri": request["target_link_uri"],
            "login_hint": request["login_hint"],
            "state": create_secure_hash()
        }
