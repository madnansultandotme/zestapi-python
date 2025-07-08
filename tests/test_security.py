"""
Tests for ZestAPI security features.
"""

from zestapi.core.security import JWTAuthBackend, create_access_token


class TestSecurity:
    """Test cases for ZestAPI security features."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        payload = {"sub": "user123", "role": "admin"}
        token = create_access_token(payload)
        assert token is not None
        assert isinstance(token, str)

    def test_jwt_auth_backend(self):
        """Test JWT authentication backend."""
        backend = JWTAuthBackend()
        assert backend is not None
