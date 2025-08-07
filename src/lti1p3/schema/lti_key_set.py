from dataclasses import dataclass
from typing import Protocol

from joserfc.jwk import Key


@dataclass(frozen=True)
class LtiKeySet:
    identifier: str
    tool_id: str
    keys: list[Key]


class KeyProvider(Protocol):
    def get_private_key(self, tool_id: str):
        ...
