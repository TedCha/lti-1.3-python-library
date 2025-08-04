import json
import time
import urllib.request
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode

from joserfc import jwt
from joserfc.jwk import KeySet
from joserfc.jwt import JWTClaimsRegistry

from lti1p3.exception import LtiException, LtiExceptionType
from lti1p3.helpers import generate_token
from lti1p3.schema.lti_registration import LtiRegistrationRepository
from lti1p3.schema.session import SessionRepository

LTI_SESSION_KEY_PREFIX = "lti1p3-"
LTI_SESSION_OIDC_LOGIN_DATA_KEY = LTI_SESSION_KEY_PREFIX + "login"


def fetch_openid_configuration(openid_config_url: str, token: str = None) -> dict:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        req = urllib.request.Request(openid_config_url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()
            return json.loads(content.decode("utf-8"))
    except HTTPError as e:
        raise LtiException(
            LtiExceptionType.FAILED_TO_FETCH_OIDC_CONFIG,
            message="failed to fetch oidc configuration because of HTTP error",
            openid_config_url=openid_config_url,
        ) from e
    except URLError as e:
        if isinstance(e.reason, TimeoutError):
            raise LtiException(
                LtiExceptionType.FAILED_TO_FETCH_OIDC_CONFIG,
                message="failed to fetch oidc configuration because of timeout",
                openid_config_url=openid_config_url,
            ) from e
        else:
            raise LtiException(
                LtiExceptionType.FAILED_TO_FETCH_OIDC_CONFIG,
                message="failed to fetch oidc configuration because of network error",
                openid_config_url=openid_config_url,
            ) from e


def fetch_jwks(jwks_url: str):
    headers = {"Accept": "application/json"}

    try:
        req = urllib.request.Request(jwks_url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()
            return json.loads(content.decode("utf-8"))
    except HTTPError as e:
        raise LtiException(
            LtiExceptionType.FAILED_TO_FETCH_JWKS,
            message="failed to fetch jwks because of HTTP error",
            jwks_url=jwks_url,
        ) from e
    except URLError as e:
        if isinstance(e.reason, TimeoutError):
            raise LtiException(
                LtiExceptionType.FAILED_TO_FETCH_JWKS,
                message="failed to fetch jwks because of timeout",
                jwks_url=jwks_url,
            ) from e
        else:
            raise LtiException(
                LtiExceptionType.FAILED_TO_FETCH_JWKS,
                message="failed to fetch jwks because of network error",
                jwks_url=jwks_url,
            ) from e


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


def _validate_platform_originating_authentication_response(launch_request: dict, session_login_data: dict):
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

    if time.time() > session_login_data["expires_at"]:
        raise LtiException(LtiExceptionType.EXPIRED_LOGIN_DATA, message="invalid login data")


def _validate_state(launch_request: dict, session_login_data: dict):
    """
    Validates the OAuth2 state parameter.

    Raises:
        LtiException
    """

    received_state = launch_request["state"]
    if received_state != session_login_data["state"]:
        raise LtiException(LtiExceptionType.INVALID_STATE, message="invalid state parameter")


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

    # TODO: Need to figure out how deployment_ids should be used
    # deployment_id = login_request["lti_deployment_id"]
    # if deployment_id and not registration.has_deployment_id(deployment_id):
    #     raise LtiException(LtiExceptionType.NO_DEPLOYMENT, message="deployment not found for registration")

    # Create state and nonce tokens and persist them in the session to be used for validation during launch
    # See: https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
    state_token = generate_token()
    nonce_token = generate_token()

    session_repository.set(LTI_SESSION_OIDC_LOGIN_DATA_KEY, {
        "state": state_token,
        "nonce": nonce_token,
        "registration_id": registration.identifier,  # Used to look up the registration during launch
        "expires_at": time.time() + 300  # Expires in 5 minutes
    })

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
    url = f"{registration.authentication_url}?{auth_query}"

    return url


def validate_oidc_authentication_response(
        launch_request: dict,
        registration_repository: LtiRegistrationRepository,
        session_repository: SessionRepository
):
    """
    Validates the OIDC authentication response. Expected to be used during LTI launch.
    """

    # Retrieve OIDC login data
    login_data = session_repository.get(LTI_SESSION_OIDC_LOGIN_DATA_KEY)

    # Preliminary validation
    _validate_platform_originating_authentication_response(launch_request, login_data)
    _validate_state(launch_request, login_data)

    registration = registration_repository.find(login_data["registration_id"])
    if not registration:
        raise LtiException(LtiExceptionType.NO_REGISTRATION, message="registration not found")

    # Fetch JWKs from the registration jwks_url
    jwks = fetch_jwks(registration.jwks_url)
    key_set = KeySet.import_key_set(jwks)

    # Create individual claim requests to be validated (exp, nbf, iat, iss, aud, azp, nonce)
    # See: https://www.imsglobal.org/spec/security/v1p0/#authentication-response-validation
    # See: https://openid.net/specs/openid-connect-core-1_0.html#IndividualClaimsRequests
    claims_request = JWTClaimsRegistry(
        iss={"essential": True, "value": registration.issuer},
        aud={"essential": True, "value": registration.client_id},
        azp={"essential": True, "value": registration.client_id, "allow_blank": True},
        nonce={"essential": True, "value": login_data["nonce"]},
    )

    # Decode the jwt
    token = jwt.decode(launch_request["id_token"], key_set)

    # Validate token claims
    claims_request.validate(token.claims)

    # TODO: Need to figure out what to do with launch data (how does it extend to adapters?)
    print(token)
