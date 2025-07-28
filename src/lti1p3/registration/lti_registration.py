class LtiRegistration:
    """
    See: http://www.imsglobal.org/spec/lti/v1p3/#tool-deployment-0
    """

    def __init__(
            self,
            identifier: str,
            client_id: str,
            platform: str,
            tool: str,
            deployment_ids: list[str],
            platform_key_chain: ...,  # TODO: Might not need, could only support jwks_url
            tool_key_chain: ...,  # TODO: Might not need, could only support jwks_url
            platform_jwks_url: str,
            tool_jwks_url: str,
    ):
        self._identifier = identifier
        self._client_id = client_id
        self._platform = platform
        self._tool = tool
        self._deployment_ids = deployment_ids
        self._platform_key_chain = platform_key_chain
        self._tool_key_chain = tool_key_chain
        self._platform_jwks_url = platform_jwks_url
        self._tool_jwks_url = tool_jwks_url

    @property
    def identifier(self):
        return self._identifier

    @property
    def client_id(self):
        return self._client_id

    @property
    def platform(self):
        return self._platform

    @property
    def tool(self):
        return self._tool

    @property
    def deployment_ids(self):
        return self._deployment_ids

    def has_deployment_id(self, value: str):
        return value in self._deployment_ids

    def get_default_deployment_id(self) -> str:
        return self._deployment_ids[0]

    @property
    def platform_key_chain(self):
        return self._platform_key_chain

    @property
    def tool_key_chain(self):
        return self._tool_key_chain

    @property
    def platform_jwks_url(self):
        return self._platform_jwks_url

    @property
    def tool_jwks_url(self):
        return self._tool_jwks_url
