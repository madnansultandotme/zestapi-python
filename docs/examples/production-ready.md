# Production Ready Example

A production-ready ZestAPI application demonstrating best practices for deployment.

## Features

- Environment-based configuration
- JWT authentication
- Rate limiting
- Comprehensive error handling
- Health checks and monitoring
- Docker support
- Logging and metrics

## Setup

```bash
cp .env.example .env
# Edit .env with your configuration
pip install -r requirements.txt
python main.py
```

## Production Deployment

### Docker
```bash
docker build -t zestapi-production .
docker run -p 8000:8000 --env-file .env zestapi-production
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
JWT_SECRET=your-super-secure-production-secret-key
DEBUG=false
LOG_LEVEL=WARNING
RATE_LIMIT=1000/minute
CORS_ORIGINS=["https://yourdomain.com"]
```

## API Endpoints

- `GET /health` - Health check with system status
- `GET /metrics` - Application metrics
- `POST /auth/login` - User authentication
- `GET /protected` - Protected route (requires JWT)
- `GET /api/v1/users` - User management (protected)

## Security Features

- JWT authentication with secure defaults
- Rate limiting per endpoint
- CORS configuration
- Input validation
- Error sanitization in production
