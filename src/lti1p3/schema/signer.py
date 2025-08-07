from typing import Protocol


class SignerProvider(Protocol):
    def sign(self, message: bytes) -> bytes:
        ...
