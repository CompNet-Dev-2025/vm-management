from flask import request, jsonify, g
from jose import jwt, jwk
from jose.utils import base64url_decode
from jose import JWTError
from jose.jwk import PyJWKClient
from functools import wraps
import os

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM = os.getenv("KEYCLOAK_REALM")
AUDIENCE = os.getenv("KEYCLOAK_AUDIENCE")
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"

jwk_client = PyJWKClient(JWKS_URL)

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", None)
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Invalid Authorization header"}), 401

        token = auth.split()[1]
        try:
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=AUDIENCE,
                issuer=f"{KEYCLOAK_URL}/realms/{REALM}"
            )
            g.user = payload
        except JWTError as e:
            return jsonify({"error": "Invalid token", "details": str(e)}), 401

        return f(*args, **kwargs)
    return wrapper

def enforce_student_identity(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        student_id = kwargs.get("student_id")
        user_id = g.user.get("preferred_username")
        if student_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return wrapper
