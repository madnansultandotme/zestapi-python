# Plugin System Example

This example demonstrates how to create and use plugins in ZestAPI.

## Features

- **Example Plugin**: A complete plugin implementation with middleware
- **Plugin Registration**: How to register and configure plugins
- **Custom Middleware**: Plugin-based middleware for request processing
- **Configuration**: Environment and file-based plugin configuration
- **Lifecycle Management**: Plugin initialization and cleanup

## Included Plugins

### Request Logger Plugin
- Logs all incoming requests with timestamps
- Configurable log levels and formats
- Request/response timing
- Custom headers injection

### API Key Authentication Plugin
- Simple API key authentication
- Configurable API keys
- Request filtering based on paths
- Custom error responses

## Plugin Structure

```
app/plugins/example_plugin/
├── __init__.py          # Plugin exports
├── plugin.py            # Main plugin class
├── middleware.py        # Custom middleware
├── config.py           # Configuration
└── README.md           # Plugin documentation
```

## Running

```bash
cd examples/plugin-system
pip install -r requirements.txt
python main.py
```

## Testing the Plugins

### Test Request Logging
```bash
curl http://localhost:8000/
curl http://localhost:8000/api/test
```

### Test API Key Authentication
```bash
# Without API key (should fail)
curl http://localhost:8000/protected

# With API key (should succeed)
curl -H "X-API-Key: test-api-key-123" http://localhost:8000/protected
```

## Configuration

Plugins can be configured via environment variables:

```bash
export LOGGER_PLUGIN_LEVEL=DEBUG
export API_KEY_PLUGIN_KEYS=key1,key2,key3
export API_KEY_PLUGIN_HEADER=X-Custom-API-Key
```

Or via configuration files (see config/ directory).
