# Authentication Example

A complete authentication system demonstrating login/signup functionality with JWT tokens.

## Features

- User registration and login
- JWT token authentication  
- Password hashing with bcrypt
- Protected routes
- Token refresh functionality
- User profile management

## Setup

```bash
cd auth-example/
pip install -r requirements.txt
python main.py
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - Logout user

### Protected Routes
- `GET /profile` - Get user profile (requires JWT)
- `PUT /profile` - Update user profile (requires JWT)
- `GET /protected` - Example protected route

## Usage Examples

### Sign Up
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com", 
    "password": "secure_password123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }'
```

### Access Protected Route
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/profile
```

## Security Features

- Passwords hashed with bcrypt
- JWT tokens with expiration
- Secure token validation
- Input validation with Pydantic
- Rate limiting on auth endpoints
