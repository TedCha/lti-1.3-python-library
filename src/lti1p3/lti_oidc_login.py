from lti1p3.helpers import create_secure_hash, build_url_with_query_params
from lti1p3.interfaces.cache import Cache
from lti1p3.interfaces.cookie import Cookie
from lti1p3.interfaces.database import Database


class OidcException(Exception):
    pass


class LtiOidcLogin:
    COOKIE_PREFIX = "lti1p3_"
    ERROR_MSG_LAUNCH_URL = "No launch URL configured"
    ERROR_MSG_ISSUER = "Could not find issuer"
    ERROR_MSG_LOGIN_HINT = "Could not find login hint"

    _db: Database
    _cache: Cache
    _cookie: Cookie

    def __init__(self, db: Database, cache: Cache, cookie: Cookie):
        self._db = db
        self._cache = cache
        self._cookie = cookie

    # TODO: Maybe convert dict into defined type
    def get_redirect_url(self, launch_url: str, request: dict[str, str]):
        # Validate request data
        registration = self.validate_oidc_login(request)

        auth_params = self.get_auth_params(launch_url, registration.client_id, request)

        return build_url_with_query_params(registration.auth_login_url, auth_params)

    def validate_oidc_login(self, request: dict[str, str]):
        if "iss" not in request:
            raise OidcException(LtiOidcLogin.ERROR_MSG_ISSUER)

        if "login_hint" not in request:
            raise OidcException(LtiOidcLogin.ERROR_MSG_LOGIN_HINT)

        # Fetch registration
        client_id = request["client_id"]
        registration = self._db.find_registration_by_issuer(request["iss"], client_id)

        if registration is None:
            ...  # TODO: Registration error msg
            raise OidcException("TODO: registration error message")

        return registration

    def get_auth_params(self, launch_url: str, client_id: str, request: dict[str, str]):
        # Set cookie (short-lived)
        state = create_secure_hash(prefix='state-')
        self._cookie.set_cookie(LtiOidcLogin.COOKIE_PREFIX, state, 60)

        nonce = create_secure_hash(prefix='nonce-')
        self._cache.cache_nonce(nonce, client_id)

        auth_params = {
            "scope": 'openid',  # OIDC Scope.
            "response_type": 'id_token',  # OIDC response is always an id token.
            "response_mode": 'form_post',  # OIDC response is always a form post.
            "prompt": 'none',  # Don't prompt user on redirect.
            "client_id": client_id,  # Registered client id.
            "redirect_uri": launch_url,  # URL to return to after login.
            "state": state,  # State to identify browser session.
            "nonce": nonce,  # Prevent replay attacks.
            "login_hint": request['login_hint'],  # Login hint to identify platform session.
        }

        if "lti_message_hint" in request:
            # LTI message hint to identify LTI context within the platform
            auth_params["lti_message_hint"] = request['lti_message_hint']

        return auth_params
