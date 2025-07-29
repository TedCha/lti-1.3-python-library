from urllib.parse import urlencode

from lti1p3.exception import LtiException, LtiExceptionType
from lti1p3.helpers import generate_token
from lti1p3.registration.lti_registration_repository import LtiRegistrationRepository

# TODO: Need to implement a cookie interface and
#  pass to this class in order to store state and nonce
class LtiOidcLogin:
    def __init__(self, registration_repository: LtiRegistrationRepository):
        self._registration_repository = registration_repository

    @staticmethod
    def _validate_oidc_login_request(request: dict):
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

    def initialize(self, request: dict):
        """
        See: https://www.imsglobal.org/spec/security/v1p1#step-2-authentication-request
        """
        self._validate_oidc_login_request(request)

        registration = self._registration_repository.find_by_tool_issuer(request["iss"], request["client_id"])

        if not registration:
            raise LtiException(LtiExceptionType.NO_REGISTRATION, message="registration not found")

        tool_key_set = registration.tool_key_set

        if not tool_key_set:
            raise LtiException(
                LtiExceptionType.NO_TOOL_KEY_SET,
                message="registration does not have a configured tool key set",
                identifier=registration.identifier
            )

        deployment_id = request["lti_deployment_id"]
        if deployment_id and not registration.has_deployment_id(deployment_id):
            raise LtiException(LtiExceptionType.NO_DEPLOYMENT, message="deployment not found for registration")

        auth_params = {
            "scope": "openid",
            "response_type": "id_token",
            "client_id": request["client_id"],
            "redirect_uri": request["target_link_uri"],
            "login_hint": request["login_hint"],
            "state": generate_token(),
            "response_mode": "form_post",
            "nonce": generate_token(),
            "prompt": "none",

        }

        # Append lti_message_hint if provided in the ODIC login request
        # See: https://www.imsglobal.org/spec/lti/v1p3#lti_message_hint-login-parameter
        if "lti_message_hint" in request:
            auth_params["lti_message_hint"] = request["lti_message_hint"]

        auth_query = urlencode(auth_params)
        url = f"{registration.platform.oidc_authentication_url}?{auth_query}"

        return url