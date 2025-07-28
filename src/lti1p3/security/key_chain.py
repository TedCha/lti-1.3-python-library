from dataclasses import dataclass


# TODO: Stuck on implementing the key/key chain model. Currently looking into if there's a library
# to perform the OIDC stuff
@dataclass(frozen=True)
class KeyChain:
    identifier: str
    key_set_name: str
    is_active: str
    public_key: str
    private_key: str
