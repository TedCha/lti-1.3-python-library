import hashlib
import os
from urllib.parse import urlparse, urlencode


def create_secure_hash(string: str = "", prefix: str = "", ):
    hash_string = string or os.urandom(64)
    hash_digest = hashlib.sha256(hash_string).hexdigest()

    return prefix + hash_digest


def build_url_with_query_params(url: str, params: dict) -> str:
    if not params:
        return url

    parsed_url = urlparse(url)
    seperator = "&" if parsed_url.query else "?"

    return url + seperator + urlencode(params)
