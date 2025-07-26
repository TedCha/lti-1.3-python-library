from lti1p3.helpers import create_secure_hash


class LtiRegistration:
    issuer: str | None
    client_id: str | None
    key_set_url: str | None
    auth_token_url: str | None
    auth_login_url: str | None
    auth_server: str | None
    tool_private_key: str | None
    kid: str | None

    def __init__(self, registration: dict[str, str]):
        self.issuer = registration["issuer"]
        self.client_id = registration["client_id"]
        self.key_set_url = registration["key_set_url"]
        self.auth_token_url = registration["auth_token_url"]
        self.auth_login_url = registration["auth_login_url"]
        self.auth_server = registration["auth_server"]
        self.tool_private_key = registration["tool_private_key"]
        self.kid = registration["kid"]

    @property
    def auth_server(self) -> str:
        return self.auth_server or self.auth_login_url

    @auth_server.setter
    def auth_server(self, value: str):
        self.auth_server = value

    @property
    def kid(self) -> str:
        return self.kid or create_secure_hash(self.issuer + self.client_id)

    @kid.setter
    def kid(self, value: str):
        self.kid = value
