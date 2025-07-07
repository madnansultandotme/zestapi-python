# ZestAPI Production Example

This example demonstrates how to deploy ZestAPI in production with proper security and configuration.

## Production Setup

### 1. Environment Configuration

Create a `.env` file:
```bash
# Security
JWT_SECRET=your-super-secure-production-secret-key-here
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=WARNING

# Rate Limiting
RATE_LIMIT=1000/minute

# CORS (adjust for your domains)
CORS_ORIGINS=["https://yourdomain.com", "https://api.yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS=["*"]
```

### 2. Production Application

```python
# main.py - Production Ready
from zestapi import ZestAPI, Settings
import os
import logging

# Production settings
settings = Settings()

# Validate critical settings
if not settings.jwt_secret or settings.jwt_secret == "your-secret-key":
    raise ValueError("JWT_SECRET must be set for production")

if settings.debug:
    raise ValueError("DEBUG must be False in production")

# Create application
app_instance = ZestAPI(
    settings=settings,
    routes_dir="app/routes",
    plugins_dir="app/plugins"
)

# Add custom error handlers for production
async def server_error_handler(request, exc):
    logger = logging.getLogger(__name__)
    logger.error(f"Server error: {exc}", exc_info=True)
    return {
        "error": {
            "code": 500,
            "message": "Internal server error",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    }

app_instance.add_exception_handler(Exception, server_error_handler)

# Get ASGI application for deployment
app = app_instance.app

if __name__ == "__main__":
    app_instance.run()
```

### 3. Docker Production Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 4. Production Requirements

```txt
# requirements.txt
zestapi>=1.0.0
uvicorn[standard]>=0.30.0
gunicorn>=21.0.0
python-dotenv>=1.0.0

# Optional production dependencies
redis>=5.0.0
asyncpg>=0.29.0
httpx>=0.25.0
```

### 5. Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  zestapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - DEBUG=false
      - LOG_LEVEL=INFO
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 128M

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - zestapi
    restart: unless-stopped

volumes:
  postgres_data:
```

### 6. Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream zestapi {
        server zestapi:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://zestapi;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            access_log off;
            proxy_pass http://zestapi;
        }
    }
}
```

### 7. Kubernetes Deployment

```yaml
# k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zestapi
spec:
  replicas: 3
  selector:
    matchLabels:
      app: zestapi
  template:
    metadata:
      labels:
        app: zestapi
    spec:
      containers:
      - name: zestapi
        image: your-registry/zestapi:latest
        ports:
        - containerPort: 8000
        env:
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: zestapi-secrets
              key: jwt-secret
        - name: DEBUG
          value: "false"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: zestapi-service
spec:
  selector:
    app: zestapi
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### 8. Production Routes Example

```python
# app/routes/api.py - Production API Routes
from zestapi import route, ORJSONResponse
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: float

@route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for load balancers"""
    import time
    return ORJSONResponse({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    })

@route("/api/v1/metrics", methods=["GET"])
async def metrics(request):
    """Basic metrics endpoint"""
    return ORJSONResponse({
        "requests_total": 1000,
        "errors_total": 5,
        "uptime_seconds": 3600
    })

class CreateItemRequest(BaseModel):
    name: str
    description: str
    price: float

@route("/api/v1/items", methods=["POST"])
async def create_item(request):
    """Create a new item with validation"""
    try:
        data = await request.json()
        item = CreateItemRequest(**data)
        
        # Process item creation
        logger.info(f"Creating item: {item.name}")
        
        return ORJSONResponse({
            "id": 1,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "created": True
        }, status_code=201)
        
    except Exception as e:
        logger.error(f"Failed to create item: {e}")
        raise
```

### 9. Monitoring and Observability

```python
# app/plugins/monitoring.py
import time
import logging
from zestapi import route, ORJSONResponse

logger = logging.getLogger(__name__)

def register(app):
    """Monitoring plugin"""
    
    @app.route("/metrics/prometheus")
    async def prometheus_metrics(request):
        """Prometheus metrics endpoint"""
        metrics = f"""
# HELP zestapi_requests_total Total number of requests
# TYPE zestapi_requests_total counter
zestapi_requests_total 1000

# HELP zestapi_request_duration_seconds Request duration
# TYPE zestapi_request_duration_seconds histogram
zestapi_request_duration_seconds_sum 100.0
zestapi_request_duration_seconds_count 1000
        """.strip()
        
        return Response(content=metrics, media_type="text/plain")

    @app.route("/debug/info")
    async def debug_info(request):
        """Debug information (only in debug mode)"""
        if not app.settings.debug:
            raise PermissionError("Debug mode disabled")
            
        import psutil
        import os
        
        return ORJSONResponse({
            "process_id": os.getpid(),
            "memory_usage": psutil.Process().memory_info().rss,
            "cpu_percent": psutil.Process().cpu_percent(),
            "uptime": time.time() - psutil.Process().create_time()
        })
```

### 10. Deployment Script

```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e

echo "🚀 Deploying ZestAPI to production..."

# Build Docker image
echo "📦 Building Docker image..."
docker build -t zestapi:latest .

# Run database migrations (if applicable)
echo "🗄️ Running database migrations..."
# python manage.py migrate

# Deploy with docker-compose
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Health check
echo "🏥 Performing health check..."
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "✅ Deployment completed successfully!"
echo "🌐 Application is running at http://localhost:8000"
```

## Security Checklist

- [ ] JWT_SECRET is set to a strong, unique value
- [ ] DEBUG is set to False
- [ ] CORS origins are properly configured
- [ ] Rate limiting is enabled
- [ ] Proper logging is configured
- [ ] SSL/TLS is enabled
- [ ] Container runs as non-root user
- [ ] Environment variables are secured
- [ ] Health checks are configured
- [ ] Resource limits are set

## Performance Optimization

1. **Use multiple workers**: `uvicorn main:app --workers 4`
2. **Enable HTTP/2**: Configure in reverse proxy
3. **Use Redis for caching**: Add Redis integration
4. **Database connection pooling**: Use asyncpg with connection pools
5. **Static file serving**: Use CDN or reverse proxy
6. **Monitoring**: Add Prometheus metrics and alerting

This production setup provides a robust, scalable, and secure deployment of ZestAPI suitable for enterprise use.
