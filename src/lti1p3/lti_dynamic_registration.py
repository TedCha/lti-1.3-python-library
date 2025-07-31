import json
import urllib.request
from urllib.error import HTTPError, URLError

from lti1p3.exception import LtiException, LtiExceptionType
from lti1p3.lti_oidc import fetch_openid_configuration

LTI_1P3_ACCESS_TOKEN_SCOPES = [
    # LTI-AGS Scopes
    'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly',
    'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem',
    'https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly',
    'https://purl.imsglobal.org/spec/lti-ags/scope/score',

    # LTI-NRPS Scopes
    'https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly',
]


def _post_registration(registration_url: str, registration_payload: dict, token: str = None) -> dict:
    body = json.dumps(registration_payload).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(registration_url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()
            return json.loads(content.decode("utf-8"))
    except HTTPError as e:
        raise LtiException(
            LtiExceptionType.FAILED_TO_FETCH_OIDC_CONFIG,
            message="failed to fetch oidc configuration because of HTTP error",
            registration_url=registration_url,
        ) from e
    except URLError as e:
        if isinstance(e.reason, TimeoutError):
            raise LtiException(
                LtiExceptionType.FAILED_TO_FETCH_OIDC_CONFIG,
                message="failed to fetch oidc configuration because of timeout",
                registration_url=registration_url,
            ) from e
        else:
            raise LtiException(
                LtiExceptionType.FAILED_TO_FETCH_OIDC_CONFIG,
                message="failed to fetch oidc configuration because of network error",
                registration_url=registration_url,
            ) from e


def register(registration_request: dict):
    openid_config_url = registration_request["openid_configuration"]
    registration_token = registration_request["registration_token"]

    open_id_config = fetch_openid_configuration(openid_config_url, registration_token)

    # TODO: Check if supports deep linking
    messages = [{"type": "LtiResourceLinkRequest"}]
    if ...:
        messages.append({"type": "LtiDeepLinkingRequest"})

    # TODO: Figure out how to constrain dynamic registration to one tool
    registration_data = {
        "application_type": "web",
        "response_types": ["id_token"],
        "grant_types": ["implicit", "client_credentials"],
        "initiate_login_url": ...,
        "redirect_uris": ...,
        "client_name": ...,
        "jwks_uri": ...,
        "logo_uri": ...,
        "token_endpoint_auth_method": "private_key_jwt",
        "scope": " ".join(LTI_1P3_ACCESS_TOKEN_SCOPES),
        "https://purl.imsglobal.org/spec/lti-tool-configuration": {
            "domain": ...,
            "description": ...,
            "target_link_uri": ...,
            "custom_parameters": ...,
            "claims": open_id_config["claims_supported"],
            "messages": messages,
        }
    }
