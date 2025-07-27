import json
import uuid
from enum import Enum
from typing import Self

import jwt.utils

from lti1p3 import lti_constants
from lti1p3.interfaces.cache import Cache
from lti1p3.interfaces.cookie import Cookie
from lti1p3.interfaces.database import Database
from lti1p3.lti_deployment import LtiDeployment
from lti1p3.lti_oidc_login import LtiOidcLogin
from lti1p3.lti_registration import LtiRegistration


class LtiMessageLaunchMessageType(Enum):
    DEEPLINK = "LtiDeepLinkingRequest"
    SUBMISSION_REVIEW = "LtiSubmissionReviewRequest"
    RESOURCE_LINK = "LtiResourceLinkRequest"


class LtiMessageLaunchExceptionType(Enum):
    UNABLE_TO_FETCH_PUBLIC_KEY = "Failed to fetch public key."
    NO_PUBLIC_KEY = "Unable to find public key."
    NO_MATCHING_PUBLIC_KEY = "Unable to find a public key which matches your JWT."
    STATE_NOT_FOUND = "Please make sure you have cookies and cross-site tracking enabled in the privacy and security settings of your browser."
    MISSING_ID_TOKEN = "Missing id_token."
    INVALID_ID_TOKEN = "Invalid id_token, JWT must contain three parts."
    MISSING_NONCE = "Missing nonce."
    INVALID_NONCE = "Invalid nonce."
    MISSING_REGISTRATION = "LTI 1.3 Registration not found. Please make sure the LMS has provided the right information, and that the LMS has been registered correctly in the tool.'"
    CLIENT_NOT_REGISTERED = "Client ID not registered for this issuer."
    NO_KID = "No KID specified in the JWT header."
    INVALID_SIGNATURE = "Invalid signature on id_token"
    MISSING_DEPLOYMENT_ID = "No deployment_id was specified."
    NO_DEPLOYMENT = "Unable to find deployment."
    INVALID_MESSAGE_TYPE = "Invalid message_type."
    UNRECOGNIZED_MESSAGE_TYPE = "Unrecognized message_type."
    INVALID_MESSAGE = "Message validation failed."
    INVALID_ALG = "Invalid algorithm was specified in the JWT header."
    MISMATCHED_ALG_KEY = "The algorithm specified in the JWT header is incompatible with the JWT key type."


class LtiMessageLaunchException(Exception):
    def __init__(self, exception_type: LtiMessageLaunchExceptionType, *, message: str = None, **kwargs):
        self.exception_type = exception_type
        self.metadata = kwargs

        if message:
            final_message = message
        elif exception_type:
            final_message = exception_type.value
        else:
            final_message = "An unknown error occurred during the LTI launch."

        super().__init__(final_message)

    @property
    def code(self):
        return self.exception_type.name if self.exception_type else "UNKNOWN"


class LtiMessageLaunch:
    request: dict
    _jwt: dict
    _registration: LtiRegistration
    _deployment: LtiDeployment

    def __init__(self, db: Database, cache: Cache, cookie: Cookie, lti_service_connector: ...):
        self._db = db
        self._cache = cache
        self._cookie = cookie
        self._lti_service_connector = lti_service_connector
        self.launch_id = f"lti1p3_launch_{uuid.uuid4().hex}"

    @classmethod
    def from_cache(
            cls,
            launch_id: str,
            db: Database,
            cache: Cache,
            cookie: Cookie,
            lti_service_connector: ...
    ) -> Self:
        new = cls(db, cache, cookie, lti_service_connector)
        new.launch_id = launch_id
        new._jwt = {"body": new._cache.get_launch_data(launch_id)}

        return new

    def cache_launch_data(self):
        self._cache.cache_launch_data(self.launch_id, self._jwt["body"])

    def has_nrps(self) -> bool:
        """
        Returns whether the current launch can use the Names and Roles Provisioning service.
        """
        return "context_memberships_url" in self._jwt["body"][lti_constants.NRPS_CLAIM_SERVICE]

    def get_nrps(self):
        ...

    def has_gs(self) -> bool:
        """
        Returns whether the current launch can use the Course Groups service.
        """
        return "context_groups_url" in self._jwt["body"][lti_constants.GS_CLAIM_SERVICE]

    def get_gs(self):
        ...

    def has_ags(self) -> bool:
        """
        Returns whether the current launch can use the Assignments and Grades service.
        """
        return lti_constants.AGS_CLAIM_ENDPOINT in self._jwt["body"]

    def get_ags(self):
        ...

    def is_deep_link_launch(self) -> bool:
        return self._jwt["body"][lti_constants.MESSAGE_TYPE] == LtiMessageLaunchMessageType.DEEPLINK

    def get_deep_link(self):
        ...

    def is_submission_review_launch(self) -> bool:
        return self._jwt["body"][lti_constants.MESSAGE_TYPE] == LtiMessageLaunchMessageType.SUBMISSION_REVIEW

    def is_resource_launch(self) -> bool:
        return self._jwt["body"][lti_constants.MESSAGE_TYPE] == LtiMessageLaunchMessageType.RESOURCE_LINK

    def get_launch_data(self):
        """
        Fetches the decoded body of the JWT used in the current launch
        """
        return self._jwt["body"]

    def can_migrate(self):
        ...

    def validate(self):
        """
        Validates all aspects of an incoming LTI Message Launch
        Raises:
            LtiMessageLaunchException
        """
        self.validate_state()
        self.validate_jwt_format()
        self.validate_nonce()
        self.validate_registration()
        self.validate_jwt_signature()
        self.validate_deployment()
        self.validate_message()

    def validate_state(self):
        # Check state for OIDC
        oidc_cookie_state = self._cookie.get_cookie(LtiOidcLogin.COOKIE_PREFIX + self.request["state"])

        if oidc_cookie_state != self.request["state"]:
            raise LtiMessageLaunchException(LtiMessageLaunchExceptionType.STATE_NOT_FOUND)

    def validate_jwt_format(self):
        if "id_token" not in self.request:
            raise LtiMessageLaunchException(LtiMessageLaunchExceptionType.MISSING_ID_TOKEN)

        jwt_parts = self.request["id_token"].split(".")

        if len(jwt_parts) != 3:
            raise LtiMessageLaunchException(LtiMessageLaunchExceptionType.INVALID_ID_TOKEN)

        # TODO: Don't like performing side effects in a validate function, need to revisit
        # Decode JWT headers
        self._jwt["header"] = json.loads(jwt.utils.base64url_decode(jwt_parts[0]))

        # Decode JWT body
        self._jwt["body"] = json.loads(jwt.utils.base64url_decode(jwt_parts[1]))

    def validate_nonce(self):
        if "nonce" not in self._jwt["body"]:
            raise LtiMessageLaunchException(LtiMessageLaunchExceptionType.MISSING_NONCE)

        is_valid_cache = self._cache.check_nonce_is_valid(self._jwt["body"]["nonce"], self.request["state"])
        if not is_valid_cache:
            raise LtiMessageLaunchException(LtiMessageLaunchExceptionType.INVALID_NONCE)

    def validate_registration(self):
        # Find registration
        client_id = self.get_aud()
        issuer_url = self._jwt["body"]["iss"]

        # TODO: Don't like performing side effects in a validate function, need to revisit
        self._registration = self._db.find_registration_by_issuer(issuer_url, client_id)
        if self._registration is None:
            raise LtiMessageLaunchException(
                LtiMessageLaunchExceptionType.MISSING_REGISTRATION,
                client_id=client_id,
                issuer_url=issuer_url
            )

        if client_id != self._registration.client_id:
            raise LtiMessageLaunchException(LtiMessageLaunchExceptionType.CLIENT_NOT_REGISTERED)

    def validate_jwt_signature(self):
        if "kid" not in self._jwt["header"]:
            raise LtiMessageLaunchException(LtiMessageLaunchExceptionType.NO_KID)

        # TODO: Need to go down the rabbit hole of ServiceRequest and ServiceConnector, could possibly simplify
