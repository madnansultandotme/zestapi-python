# ZestAPI Examples

This directory contains example applications demonstrating various ZestAPI features.

## Examples

### 1. [Basic API](basic-api/)
A simple REST API demonstrating basic ZestAPI usage with CRUD operations.

### 2. [Authentication Example](auth-example/)
Shows how to implement JWT authentication with protected routes.

### 3. [E-commerce API](ecommerce-api/)
A comprehensive e-commerce API with products, shopping cart, orders, and user management.

### 4. [WebSocket Chat](websocket-chat/)
Real-time chat application using WebSocket support with multiple rooms and user presence.

### 5. [Video Streaming](video-streaming/)
Real-time video streaming application using WebSockets and camera feed.

### 6. [Plugin System](plugin-system/)
Demonstrates the plugin architecture with custom middleware and extensible functionality.

### 7. [Production Ready](production-ready/)
A production-ready application with proper configuration, error handling, and monitoring.

## Running Examples

Each example includes its own `README.md` with setup instructions. Generally:

```bash
cd example-name/
pip install -r requirements.txt
python main.py
```

## Development

Use these examples as starting points for your own ZestAPI applications. Each example showcases different aspects of the framework:

- **API Design Patterns**: REST API best practices and structure
- **Authentication & Security**: JWT, API keys, rate limiting
- **Real-time Features**: WebSockets, chat, video streaming
- **Plugin Architecture**: Extensible middleware and custom functionality
- **E-commerce Patterns**: Shopping cart, orders, product management
- **Production Deployment**: Configuration, monitoring, error handling

## Example Features

| Example | Features |
|---------|----------|
| Basic API | CRUD operations, Pydantic validation, file-based routing |
| Authentication | JWT auth, password hashing, protected routes, user management |
| E-commerce API | Products, cart, orders, inventory, search, categories |
| WebSocket Chat | Real-time messaging, multiple rooms, user presence, typing indicators |
| Video Streaming | Camera capture, real-time streaming, multiple viewers, quality control |
| Plugin System | Custom middleware, plugin lifecycle, configuration, extensibility |
| Production Ready | Health checks, metrics, logging, error handling, configuration |

## Quick Start

To quickly explore ZestAPI features:

1. **Start with Basic API** for fundamental concepts
2. **Try Authentication Example** for security patterns  
3. **Explore E-commerce API** for complex business logic
4. **Experiment with WebSocket Chat** for real-time features
5. **Test Video Streaming** for multimedia applications
6. **Study Plugin System** for extensibility patterns
