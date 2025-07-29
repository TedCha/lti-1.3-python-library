import secrets
import base64

def generate_token(length: int = 32) -> str:
    # Generate a secure random byte string
    random_bytes = secrets.token_bytes(length)
    # Encode it in URL-safe base64 format
    token = base64.urlsafe_b64encode(random_bytes).rstrip(b'=').decode('utf-8')

    return token

