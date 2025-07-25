import hashlib
import os


class OidcException(Exception):
    pass

class LtiOidcLogin:
    COOKIE_PREFIX = "lti1p3_"
    ERROR_MSG_LAUNCH_URL = "No launch URL configured"
    ERROR_MSG_ISSUER = "Could not find issuer"
    ERROR_MSG_LOGIN_HINT = "Could not find login hint"

    # TODO: Define interface types
    def __init__(self, db, cache, cookie):
        self._db = db
        self._cache = cache
        self._cookie = cookie

    # TODO: Maybe convert dict into defined type
    def get_redirect_url(self, launch_url: str, request: dict[str, str]):
        # Validate request data
        registration = self.validate_oidc_login(request)

        auth_params = self.get_auth_params(launch_url, registration.client_id, request)

        # TODO: Create type for registration and build buildUrlWithQueryParams helper
        return registration.get_auth_login_url()

    def validate_oidc_login(self, request: dict[str, str]):
        if "iss" not in request:
            raise OidcException(LtiOidcLogin.ERROR_MSG_ISSUER)

        if "login_hint" not in request:
            raise OidcException(LtiOidcLogin.ERROR_MSG_LOGIN_HINT)

        # Fetch registration
        client_id = request["client_id"]
        registration = self._db.find_registration_by_issuer(request["iss"], client_id)

        if registration is None:
            ... # TODO: Registration error msg
            raise OidcException("TODO: registration error message")

        return registration


    def get_auth_params(self, launch_url: str, client_id: str, request: dict[str, str]):
        # Set cookie (short-lived)
        state = LtiOidcLogin.secure_random_string('state-')
        self._cookie.set_cookie(LtiOidcLogin.COOKIE_PREFIX, state, 60)

        nonce = LtiOidcLogin.secure_random_string('nonce-')
        self._cache.cache_nonce(nonce, client_id)

        auth_params = {
            "scope": 'openid', # OIDC Scope.
            "response_type": 'id_token', # OIDC response is always an id token.
            "response_mode": 'form_post', # OIDC response is always a form post.
            "prompt": 'none', # Don't prompt user on redirect.
            "client_id": client_id, # Registered client id.
            "redirect_uri": launch_url, # URL to return to after login.
            "state": state, # State to identify browser session.
            "nonce": nonce, # Prevent replay attacks.
            "login_hint": request['login_hint'], # Login hint to identify platform session.
        }

        if "lti_message_hint" in request:
            # LTI message hint to identify LTI context within the platform
            auth_params["lti_message_hint"] = request['lti_message_hint']

        return auth_params


    # TODO: Think about putting in util directory
    @staticmethod
    def secure_random_string(prefix: str = ""):
        random_bytes = os.urandom(64)
        hash_digest = hashlib.sha256(random_bytes).hexdigest()

        return prefix + hash_digest