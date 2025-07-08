"""
Conftest file for pytest configuration and shared fixtures.
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest

from zestapi import ZestAPI
from zestapi.core.application import ZestAPI as ZestAPICore


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def app() -> AsyncGenerator[ZestAPICore, None]:
    """Create a test ZestAPI application instance."""
    test_app = ZestAPI()
    yield test_app


@pytest.fixture
async def client(app: ZestAPICore):
    """Create a test client for the ZestAPI application."""
    import httpx
    from httpx import AsyncClient

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app.app), base_url="http://testserver"
    ) as client:
        yield client
        yield client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {"name": "John Doe", "email": "john@example.com", "age": 30}


@pytest.fixture
def jwt_secret():
    """JWT secret for testing."""
    return "test-secret-key-for-testing-only"
