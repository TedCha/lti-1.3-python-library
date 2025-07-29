from typing import Protocol

# TODO: Notes about how this is generic to allow for cookies or localStorage to be used
class KeyValueRepository(Protocol):
    def get(self, key: str) -> str | None:
        ...

    def set(self, key: str, value: str) -> None:
        ...

    def delete(self, key: str) -> None:
        ...