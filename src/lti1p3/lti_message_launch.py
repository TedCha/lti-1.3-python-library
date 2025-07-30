import jwt

from lti1p3.exception import LtiException, LtiExceptionType
from lti1p3.session_repository import SessionRepository
from lti1p3.registration.lti_registration_repository import LtiRegistrationRepository


class LtiMessageLaunch:
    def __init__(
            self,
            registration_repository: LtiRegistrationRepository,
            session_repository: SessionRepository
    ):
        self._registration_repository = registration_repository
        self._session_repository = session_repository

    def launch(self, request: dict):
        self._validate_platform_originating_launch_request(request)
        state_claims = self.validate_and_extract_state_claims(request)

        registration = self._registration_repository.find_by_platform_issuer(state_claims["iss"], state_claims["client_id"])
        if not registration:
            raise LtiException(LtiExceptionType.NO_REGISTRATION, message="registration not found")

        # Get the platform signing key from the jwks url of the tool registration
        jwks_client = jwt.PyJWKClient(registration.platform_jwks_url)
        platform_signing_key = jwks_client.get_signing_key_from_jwt(request["id_token"])

        # Decode and verify the id_token; decode_complete verifies the following claims:
        # exp, nbf, iat, aud, iss, sub, jti
        # See: https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
        lti_data = jwt.decode_complete(
            request["id_token"],
            key=platform_signing_key,
            audience=request["client_id"],
            algorithms=[platform_signing_key.algorithm_name] # TODO: Need to make sure that it's okay to use the algo specified in JWKS
        )

        lti_payload = lti_data["payload"]

        # Validate the nonce
        # See: https://openid.net/specs/openid-connect-core-1_0.html#ImplicitIDTValidation
        self.validate_nonce(lti_payload)

        # TODO: Need to figure out what to do with launch data (how does it extend to adapters?)
        print(lti_payload)

    @staticmethod
    def _validate_platform_originating_launch_request(request: dict):
        """
        Validates the launch request.

        Raises:
            LtiException
        """
        if "state" not in request:
            raise LtiException(LtiExceptionType.MISSING_STATE, message="missing state")

        if "id_token" not in request:
            raise LtiException(LtiExceptionType.MISSING_ID_TOKEN, message="missing id_token")

    def validate_and_extract_state_claims(self, request: dict):
        """
        Validates the OAuth2 state parameter and extracts claims from the encoded JWT value.

        Returns:
            dict: Decoded state payload with 'iss' and 'client_id'

        Raises:
            LtiException
        """
        received_state = request["state"]
        session_state = self._session_repository.get("lti1p3-state")

        if received_state != session_state:
            raise LtiException(LtiExceptionType.INVALID_STATE, message="invalid state parameter")

        # TODO: Need to implement the tool-wide signing key
        state_payload = jwt.decode(session_state, ..., algorithm="HS256")

        if "iss" not in state_payload:
            raise LtiException(LtiExceptionType.INVALID_STATE, message="invalid state parameter")

        if "client_id" not in state_payload:
            raise LtiException(LtiExceptionType.INVALID_STATE, message="invalid state parameter")

        return { "iss": state_payload["iss"], "client_id": state_payload["client_id"] }

    def validate_nonce(self, jwt_payload: dict):
        received_nonce = jwt_payload["nonce"]
        session_nonce = self._session_repository.get("lti1p3-nonce")

        # TODO: Need to explore if nonce should be encoded as JWT with expiration time
        if received_nonce != session_nonce:
            raise LtiException(LtiExceptionType.INVALID_NONCE, message="invalid nonce parameter")