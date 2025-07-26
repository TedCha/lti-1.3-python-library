from typing import Protocol


class Cookie(Protocol):
    def get_cookie(self, name: str) -> str | None:
        ...

    def set_cookie(self, name: str, value: str, expires: int, options: [str]):
        ...
