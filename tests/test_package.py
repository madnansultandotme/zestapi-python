import os
import tempfile
from datetime import timedelta

import pytest
from starlette.testclient import TestClient

from zestapi import ORJSONResponse, ZestAPI, create_access_token, route
from zestapi.core.settings import Settings


class TestZestAPIPackage:

    def test_basic_app_creation(self):
        """Test basic ZestAPI application creation"""
        app_instance = ZestAPI()
        app = app_instance.create_app()
        assert app is not None

    def test_route_decorator(self):
        """Test the route decorator functionality"""
        app_instance = ZestAPI()

        @route("/test")
        async def test_endpoint(request):
            return ORJSONResponse({"test": "success"})

        app_instance.add_route("/test", test_endpoint)
        app = app_instance.create_app()

        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"test": "success"}

    def test_orjson_response(self):
        """Test ORJSONResponse functionality"""
        app_instance = ZestAPI()

        @route("/json")
        async def json_endpoint(request):
            return ORJSONResponse(
                {
                    "string": "test",
                    "number": 42,
                    "boolean": True,
                    "array": [1, 2, 3],
                    "object": {"nested": "value"},
                }
            )

        app_instance.add_route("/json", json_endpoint)
        app = app_instance.create_app()

        client = TestClient(app)
        response = client.get("/json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert data["string"] == "test"
        assert data["number"] == 42
        assert data["boolean"] is True
        assert data["array"] == [1, 2, 3]
        assert data["object"]["nested"] == "value"

    def test_jwt_token_creation(self):
        """Test JWT token creation"""
        token = create_access_token(
            data={"sub": "testuser", "role": "admin"},
            expires_delta=timedelta(minutes=30),
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_custom_settings(self):
        """Test custom settings configuration"""
        settings = Settings()
        settings.host = "127.0.0.1"
        settings.port = 9000
        settings.rate_limit = "50/minute"

        app_instance = ZestAPI(settings=settings)
        assert app_instance.settings.host == "127.0.0.1"
        assert app_instance.settings.port == 9000
        assert app_instance.settings.rate_limit == "50/minute"

    def test_route_discovery(self):
        """Test automatic route discovery from directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            routes_dir = os.path.join(temp_dir, "routes")
            os.makedirs(routes_dir)

            # Create a test route file
            route_file = os.path.join(routes_dir, "test_routes.py")
            with open(route_file, "w") as f:
                f.write(
                    """
from zestapi import route, ORJSONResponse

@route("/discovered", methods=["GET"])
async def discovered_route(request):
    return ORJSONResponse({"discovered": True})
"""
                )

            app_instance = ZestAPI(routes_dir=routes_dir)
            app = app_instance.create_app()

            client = TestClient(app)
            response = client.get("/discovered")
            assert response.status_code == 200
            assert response.json() == {"discovered": True}

    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        app_instance = ZestAPI()

        @route("/cors-test")
        async def cors_endpoint(request):
            return ORJSONResponse({"cors": "test"})

        app_instance.add_route("/cors-test", cors_endpoint)
        app = app_instance.create_app()

        client = TestClient(app)

        # Test preflight request
        response = client.options(
            "/cors-test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Should handle OPTIONS request
        assert response.status_code in [200, 204]

    def test_rate_limiting_headers(self):
        """Test rate limiting headers are present"""
        settings = Settings()
        settings.rate_limit = "10/minute"

        app_instance = ZestAPI(settings=settings)

        @route("/rate-test")
        async def rate_endpoint(request):
            return ORJSONResponse({"rate": "test"})

        app_instance.add_route("/rate-test", rate_endpoint)
        app = app_instance.create_app()

        client = TestClient(app)
        response = client.get("/rate-test")

        assert response.status_code == 200
        assert "x-ratelimit-limit" in response.headers
        assert "x-ratelimit-remaining" in response.headers
        assert "x-ratelimit-window" in response.headers

    def test_error_handling(self):
        """Test error handling middleware"""
        app_instance = ZestAPI()

        @route("/error-test")
        async def error_endpoint(request):
            raise ValueError("Test error")

        app_instance.add_route("/error-test", error_endpoint)
        app = app_instance.create_app()

        client = TestClient(app)
        response = client.get("/error-test")

        # ValueError now correctly maps to 400 (Bad Request)
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == 400
        assert data["error"]["type"] == "ValidationError"
        assert "request_id" in data["error"]

    def test_request_logging(self):
        """Test that requests are logged with process time"""
        app_instance = ZestAPI()

        @route("/log-test")
        async def log_endpoint(request):
            return ORJSONResponse({"logged": True})

        app_instance.add_route("/log-test", log_endpoint)
        app = app_instance.create_app()

        client = TestClient(app)
        response = client.get("/log-test")

        assert response.status_code == 200
        assert "x-process-time" in response.headers

    def test_websocket_support(self):
        """Test WebSocket route support"""
        app_instance = ZestAPI()

        async def websocket_endpoint(websocket):
            await websocket.accept()
            await websocket.send_text("Hello WebSocket!")
            await websocket.close()

        app_instance.add_websocket_route("/ws-test", websocket_endpoint)
        app = app_instance.create_app()

        client = TestClient(app)
        with client.websocket_connect("/ws-test") as websocket:
            data = websocket.receive_text()
            assert data == "Hello WebSocket!"

    def test_path_parameters(self):
        """Test path parameters extraction"""
        app_instance = ZestAPI()

        @route("/items/{item_id}")
        async def get_item(request):
            item_id = request.path_params["item_id"]
            return ORJSONResponse({"item_id": item_id})

        app_instance.add_route("/items/{item_id}", get_item)
        app = app_instance.create_app()

        client = TestClient(app)
        response = client.get("/items/123")
        assert response.status_code == 200
        assert response.json() == {"item_id": "123"}

    def test_query_parameters(self):
        """Test query parameters extraction"""
        app_instance = ZestAPI()

        @route("/search")
        async def search(request):
            query = request.query_params.get("q", "")
            limit = int(request.query_params.get("limit", "10"))
            return ORJSONResponse({"query": query, "limit": limit})

        app_instance.add_route("/search", search)
        app = app_instance.create_app()

        client = TestClient(app)
        response = client.get("/search?q=test&limit=5")
        assert response.status_code == 200
        assert response.json() == {"query": "test", "limit": 5}

    def test_post_request_with_json(self):
        """Test POST request with JSON body"""
        app_instance = ZestAPI()

        @route("/create", methods=["POST"])
        async def create_item(request):
            data = await request.json()
            return ORJSONResponse({"created": True, "data": data}, status_code=201)

        app_instance.add_route("/create", create_item, methods=["POST"])
        app = app_instance.create_app()

        client = TestClient(app)
        response = client.post("/create", json={"name": "test", "value": 42})
        assert response.status_code == 201

        data = response.json()
        assert data["created"] is True
        assert data["data"]["name"] == "test"
        assert data["data"]["value"] == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
