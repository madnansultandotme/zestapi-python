# Basic API Example

A simple REST API demonstrating ZestAPI's core features.

## Features Demonstrated

- File-based route discovery
- CRUD operations
- Request validation with Pydantic
- Error handling
- JSON responses

## Setup

```bash
cd basic-api/
pip install -r requirements.txt
python main.py
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /users` - List all users
- `GET /users/{user_id}` - Get user by ID
- `POST /users` - Create new user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

## Testing

```bash
# List users
curl http://localhost:8000/users

# Create user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'

# Get user
curl http://localhost:8000/users/1
```
