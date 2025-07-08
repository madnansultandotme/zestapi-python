try:
    import bcrypt
except ImportError:
    print("Warning: bcrypt not installed. Install with: pip install bcrypt")
    bcrypt = None

try:
    from jose import JWTError, jwt
except ImportError:
    print("Warning: python-jose not installed. Install with: pip install python-jose")
    jwt = None
    JWTError = Exception

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    if bcrypt is None:
        # Fallback to simple hashing (NOT SECURE - for demo only)
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if bcrypt is None:
        # Fallback to simple verification (NOT SECURE - for demo only)
        import hashlib
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    if jwt is None:
        raise ImportError(
            "PyJWT is required for JWT token creation. Install with: pip install PyJWT"
        )

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    if jwt is None:
        raise ImportError(
            "python-jose is required for JWT token verification. Install with: pip install python-jose"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_from_token(
    token: str, users_db: Dict[int, Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Get user from JWT token."""
    payload = verify_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return users_db.get(int(user_id))
