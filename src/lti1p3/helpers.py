import hashlib
import os


def create_secure_hash(prefix: str = "", ):
    hash_digest = hashlib.sha256(os.urandom(64)).hexdigest()

    return prefix + hash_digest
