
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from starlette.authentication import AuthCredentials, SimpleUser, AuthenticationBackend
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.requests import HTTPConnection
from .settings import settings

ALGORITHM = "HS256"

class JWTAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection):
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() == "bearer":
                payload = jwt.decode(credentials, settings.jwt_secret, algorithms=[ALGORITHM])
                username = payload.get("sub")
                if username is None:
                    return  # Return None instead of raising exception for missing subject
                return AuthCredentials(["authenticated"]), SimpleUser(username)
        except JWTError:
            return  # Return None instead of raising exception for invalid JWT
        except ValueError:
            return  # Return None instead of raising exception for invalid header format


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt


def requires_auth(func):
    func.__requires_auth__ = True
    return func


