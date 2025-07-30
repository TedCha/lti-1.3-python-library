from urllib.parse import urlencode

import jwt

from lti1p3.exception import LtiException, LtiExceptionType
from lti1p3.helpers import generate_token
from lti1p3.schema.lti_registration import LtiRegistrationRepository
from lti1p3.schema.session import SessionRepository


def _validate_oidc_login_request(request: dict):
    """
    Validates the OIDC login request.

    See: https://www.imsglobal.org/spec/security/v1p1#step-1-third-party-initiated-login

    Raises:
        LtiException
    """
    if "iss" not in request:
        raise LtiException(LtiExceptionType.MISSING_LOGIN_PARAMETERS, message="missing iss")

    if "login_hint" not in request:
        raise LtiException(LtiExceptionType.MISSING_LOGIN_PARAMETERS, message="missing login_hint")

    if "target_link_uri" not in request:
        raise LtiException(LtiExceptionType.MISSING_LOGIN_PARAMETERS, message="missing target_link_uri")


def _validate_platform_originating_authentication_response(launch_request: dict):
    """
    Validates the launch request (e.g. the authentication response).

    See: https://www.imsglobal.org/spec/security/v1p1#step-3-authentication-response

    Raises:
        LtiException
    """
    if "state" not in launch_request:
        raise LtiException(LtiExceptionType.MISSING_STATE, message="missing state")

    if "id_token" not in launch_request:
        raise LtiException(LtiExceptionType.MISSING_ID_TOKEN, message="missing id_token")


def _validate_and_extract_state_claims(launch_request: dict, session_repository: SessionRepository):
    """
    Validates the OAuth2 state parameter and extracts claims from the encoded JWT value.

    Returns:
        dict: Decoded state payload with 'iss' and 'client_id'

    Raises:
        LtiException
    """

    received_state = launch_request["state"]
    session_state = session_repository.get("lti1p3-state")

    if received_state != session_state:
        raise LtiException(LtiExceptionType.INVALID_STATE, message="invalid state parameter")

    # TODO: Need to implement the tool-wide signing key
    state_payload = jwt.decode(session_state, ..., algorithm="HS256")

    if "iss" not in state_payload:
        raise LtiException(LtiExceptionType.INVALID_STATE, message="invalid state parameter")

    if "client_id" not in state_payload:
        raise LtiException(LtiExceptionType.INVALID_STATE, message="invalid state parameter")

    return {"iss": state_payload["iss"], "client_id": state_payload["client_id"]}


def _validate_nonce(jwt_payload: dict, session_repository: SessionRepository):
    received_nonce = jwt_payload["nonce"]
    session_nonce = session_repository.get("lti1p3-nonce")

    # TODO: Need to explore if nonce should be encoded as JWT with expiration time
    if received_nonce != session_nonce:
        raise LtiException(LtiExceptionType.INVALID_NONCE, message="invalid nonce parameter")


def create_oidc_authentication_url(
        login_request: dict,
        registration_repository: LtiRegistrationRepository,
        session_repository: SessionRepository,
):
    """
    Create the OIDC authentication URL using the OIDC login request.
    See: https://www.imsglobal.org/spec/security/v1p1#step-2-authentication-request
    """

    # Validate the request
    _validate_oidc_login_request(login_request)

    registration = registration_repository.find_by_platform_issuer(login_request["iss"], login_request["client_id"])
    if not registration:
        raise LtiException(LtiExceptionType.NO_REGISTRATION, message="registration not found")

    # TODO: Need to verify if I actually need to check the tool key set here
    # tool_key_set = registration.tool_key_set
    # if not tool_key_set:
    #     raise LtiException(
    #         LtiExceptionType.NO_TOOL_KEY_SET,
    #         message="registration does not have a configured tool key set",
    #         identifier=registration.identifier
    #     )

    deployment_id = login_request["lti_deployment_id"]
    if deployment_id and not registration.has_deployment_id(deployment_id):
        raise LtiException(LtiExceptionType.NO_DEPLOYMENT, message="deployment not found for registration")

    state_payload = {
        "iss": login_request["iss"],
        "client_id": login_request["client_id"],
    }

    # Create state token as JWT token that encodes the login issuer and client_id
    # See: https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
    # TODO: Need to implement the tool-wide signing key
    state_token = jwt.encode(state_payload, ..., algorithm="HS256")

    # Persist the state token in the session repository to look up the registration during launch
    session_repository.set("lti1p3-state", state_token)

    # Create nonce token as persist the token in the session repository to look up registration during launch
    nonce_token = generate_token()
    session_repository.set("lti1p3-nonce", nonce_token)

    auth_params = {
        "scope": "openid",
        "response_type": "id_token",
        "client_id": login_request["client_id"],
        "redirect_uri": login_request["target_link_uri"],
        "login_hint": login_request["login_hint"],
        "state": state_token,
        "response_mode": "form_post",
        "nonce": nonce_token,
        "prompt": "none",
    }

    # Append lti_message_hint if provided in the ODIC login request
    # See: https://www.imsglobal.org/spec/lti/v1p3#lti_message_hint-login-parameter
    if "lti_message_hint" in login_request:
        auth_params["lti_message_hint"] = login_request["lti_message_hint"]

    auth_query = urlencode(auth_params)
    url = f"{registration.platform_authentication_url}?{auth_query}"

    return url


def validate_oidc_authentication_response(
        launch_request: dict,
        registration_repository: LtiRegistrationRepository,
        session_repository: SessionRepository
):
    """
    Validates the OIDC authentication response. Expected to be used during LTI launch.
    """
    _validate_platform_originating_authentication_response(launch_request)
    state_claims = _validate_and_extract_state_claims(launch_request, session_repository)

    registration = registration_repository.find_by_platform_issuer(state_claims["iss"], state_claims["client_id"])
    if not registration:
        raise LtiException(LtiExceptionType.NO_REGISTRATION, message="registration not found")

    # Get the platform signing key from the jwks url of the tool registration
    jwks_client = jwt.PyJWKClient(registration.platform_jwks_url)
    platform_signing_key = jwks_client.get_signing_key_from_jwt(launch_request["id_token"])

    # Decode and verify the id_token; decode_complete verifies the following claims:
    # exp, nbf, iat, aud, iss, sub, jti
    # See: https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
    lti_data = jwt.decode_complete(
        launch_request["id_token"],
        key=platform_signing_key,
        audience=launch_request["client_id"],
        algorithms=[platform_signing_key.algorithm_name]
        # TODO: Need to make sure that it's okay to use the algo specified in JWKS
    )

    lti_payload = lti_data["payload"]

    # Validate the nonce
    # See: https://openid.net/specs/openid-connect-core-1_0.html#ImplicitIDTValidation
    _validate_nonce(lti_payload, session_repository)

    # TODO: Need to figure out what to do with launch data (how does it extend to adapters?)
    print(lti_payload)
