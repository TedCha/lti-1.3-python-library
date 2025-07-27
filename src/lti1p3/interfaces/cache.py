from typing import Protocol


class Cache(Protocol):

    def get_launch_data(self, key: str) -> dict:
        ...

    def cache_launch_data(self, key: str, jwt_body: dict):
        ...

    def cache_nonce(self, nonce: str, state: str):
        ...

    def check_nonce_is_valid(self, nonce: str, state: str) -> bool:
        ...

    def get_access_token(self, key: str) -> str | None:
        ...

    def cache_access_token(self, key: str, access_token: str):
        ...

    def clear_access_token(self, key: str):
        ...
