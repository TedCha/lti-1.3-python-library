from dataclasses import dataclass


@dataclass(frozen=True)
class LtiKey:
    identifier: str
    tool_id: str
