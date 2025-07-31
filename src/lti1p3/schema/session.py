from typing import Protocol, Any


class SessionRepository(Protocol):
    def get(self, key: str) -> Any | None:
        ...

    def set(self, key: str, value: Any) -> None:
        ...

    def delete(self, key: str) -> None:
        ...
