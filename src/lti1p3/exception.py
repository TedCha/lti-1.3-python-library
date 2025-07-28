from enum import Enum, auto


class LtiExceptionType(Enum):
    MISSING_LOGIN_PARAMETERS = auto()
    NO_REGISTRATION = auto()
    NO_TOOL_KEY_CHAIN = auto()
    NO_DEPLOYMENT = auto()


class LtiException(Exception):
    def __init__(self, exception_type: LtiExceptionType, *, message: str = None, **kwargs):
        self.exception_type = exception_type
        self.metadata = kwargs

        if message:
            final_message = message
        elif exception_type:
            final_message = exception_type.name
        else:
            final_message = "An unknown error occurred during the LTI launch."

        super().__init__(final_message)

    @property
    def code(self):
        return self.exception_type.name if self.exception_type else "UNKNOWN"
