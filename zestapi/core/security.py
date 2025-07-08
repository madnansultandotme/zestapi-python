from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Tuple

from jose import JWTError, jwt
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    SimpleUser,
)
from starlette.requests import HTTPConnection

from .settings import settings

ALGORITHM = "HS256"


class JWTAuthBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> Optional[Tuple[AuthCredentials, SimpleUser]]:
        if "Authorization" not in conn.headers:
            return None

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() == "bearer":
                payload = jwt.decode(
                    credentials, settings.jwt_secret, algorithms=[ALGORITHM]
                )
                username = payload.get("sub")
                if username is None:
                    # Return None for missing subject
                    return None
                return (
                    AuthCredentials(["authenticated"]),
                    SimpleUser(username),
                )
            return None  # Invalid scheme
        except JWTError:
            # Return None instead of raising exception for invalid JWT
            return None
        except ValueError:
            # Return None for invalid header format
            return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt


def requires_auth(func: Any) -> Any:
    func.__requires_auth__ = True
    return func
