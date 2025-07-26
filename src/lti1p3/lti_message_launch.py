import uuid
from enum import Enum, auto
from typing import Self

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


class LtiMessageLunchExceptionType(Enum):
    UNABLE_TO_FETCH_PUBLIC_KEY = auto()
    NO_PUBLIC_KEY = auto()
    NO_MATCHING_PUBLIC_KEY = auto()
    STATE_NOT_FOUND = auto()
    MISSING_ID_TOKEN = auto()
    INVALID_ID_TOKEN = auto()
    MISSING_NONCE = auto()
    INVALID_NONCE = auto()
    MISSING_REGISTRATION = auto()
    CLIENT_NOT_REGISTERED = auto()
    NO_KID = auto()
    INVALID_SIGNATURE = auto()
    MISSING_DEPLOYMENT_ID = auto()
    NO_DEPLOYMENT = auto()
    INVALID_MESSAGE_TYPE = auto()
    UNRECOGNIZED_MESSAGE_TYPE = auto()
    INVALID_MESSAGE = auto()
    INVALID_ALG = auto()
    MISMATCHED_ALG_KEY = auto()


class LtiMessageLaunchException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.exception_type = kwargs.get("exception_type")


class LtiMessageLaunch:
    request: dict
    _jwt: dict
    _lti_registration: LtiRegistration
    _lti_deployment: LtiDeployment

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
            raise LtiMessageLaunchException(
                "Please make sure you have cookies and cross-site tracking enabled in the privacy and security settings of your browser",
                exception_type=LtiMessageLunchExceptionType.STATE_NOT_FOUND
            )
