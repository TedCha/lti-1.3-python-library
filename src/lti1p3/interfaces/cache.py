from typing import Protocol


class Cache(Protocol):

    def get_launch_data(self, key: str):
        ...

    def cache_launch_data(self, jwt_body):
        ...

    def cache_nonce(self, nonce: str, state: str):
        ...

    def check_nonce_is_valid(self, state: str):
        ...

    def get_access_token(self, key: str):
        ...

    def cache_access_token(self, key: str, access_token: str):
        ...

    def clear_access_token(self, key: str):
        ...
