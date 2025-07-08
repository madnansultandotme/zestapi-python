"""
Tests for ZestAPI core functionality.
"""

from zestapi import ORJSONResponse, ZestAPI


class TestZestAPICore:
    """Test cases for ZestAPI core functionality."""

    def test_app_creation(self):
        """Test that ZestAPI app can be created."""
        app = ZestAPI()
        assert app is not None
        assert hasattr(app, "app")

    def test_route_decoration(self):
        """Test route decoration functionality."""
        app = ZestAPI()

        @app.route("/test")
        async def test_endpoint(request):
            return ORJSONResponse({"message": "test"})

        # Check that route was added
        assert len(app._routes) > 0

    def test_websocket_route_decoration(self):
        """Test WebSocket route decoration."""
        app = ZestAPI()

        @app.websocket_route("/ws")
        async def websocket_endpoint(websocket):
            await websocket.accept()
            await websocket.close()

        # Check that WebSocket route was added
        ws_routes = [r for r in app._routes if getattr(r, "path", None) == "/ws"]
        assert len(ws_routes) > 0


class TestResponses:
    """Test cases for ZestAPI response types."""

    def test_orjson_response(self):
        """Test ORJSONResponse creation."""
        response = ORJSONResponse({"test": "data"})
        assert response.status_code == 200
        assert response.media_type == "application/json"

    def test_orjson_response_with_status(self):
        """Test ORJSONResponse with custom status code."""
        response = ORJSONResponse({"error": "not found"}, status_code=404)
        assert response.status_code == 404
