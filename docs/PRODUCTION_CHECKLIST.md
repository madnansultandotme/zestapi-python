# 🚀 ZestAPI Production Deployment Checklist

This checklist ensures your ZestAPI application is properly configured for production deployment.

## ✅ Pre-Deployment Checklist

### 🔐 Security Configuration
- [ ] **JWT Secret**: Set `JWT_SECRET` to a strong, unique value (minimum 32 characters)
- [ ] **Debug Mode**: Ensure `DEBUG=false` in production environment
- [ ] **CORS Origins**: Configure `CORS_ORIGINS` to specific domains (not `["*"]`)
- [ ] **Rate Limiting**: Set appropriate `RATE_LIMIT` for your use case
- [ ] **HTTPS**: Ensure your deployment uses HTTPS (SSL/TLS certificates)

### 🏗️ Environment Setup
- [ ] **Environment Variables**: All sensitive data in environment variables
- [ ] **Database Connections**: Production database configured and tested
- [ ] **Logging**: Configure appropriate `LOG_LEVEL` (WARNING or ERROR)
- [ ] **Error Monitoring**: Set up error tracking (Sentry, etc.)
- [ ] **Health Checks**: Implement `/health` endpoint for load balancers

### 📊 Performance & Monitoring
- [ ] **Resource Limits**: Configure appropriate CPU/memory limits
- [ ] **Worker Processes**: Use multiple workers for production (uvicorn/gunicorn)
- [ ] **Load Balancer**: Configure reverse proxy (Nginx, Traefik, etc.)
- [ ] **Metrics**: Set up application metrics collection
- [ ] **Alerting**: Configure alerts for errors and performance issues

### 🔄 Deployment & Operations
- [ ] **Container Security**: Use minimal base images, security scanning
- [ ] **Backup Strategy**: Regular backups of application data
- [ ] **Rolling Updates**: Zero-downtime deployment strategy
- [ ] **Rollback Plan**: Quick rollback procedure documented
- [ ] **Documentation**: Deployment and operations documentation updated

## 🛡️ Security Validation

### JWT Configuration Test
```python
# Validate JWT secret strength
import os
jwt_secret = os.getenv("JWT_SECRET", "")
assert len(jwt_secret) >= 32, "JWT_SECRET must be at least 32 characters"
assert jwt_secret != "your-secret-key", "Must use custom JWT_SECRET"
```

### CORS Configuration Test
```python
# Validate CORS settings
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
assert "*" not in cors_origins, "CORS should not allow all origins in production"
```

## 🐳 Docker Production Example

```dockerfile
FROM python:3.11-slim

# Security: Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
WORKDIR /app
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Production command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 🔧 Environment Variables Template

```bash
# Production Environment Template
# Copy to .env and customize for your environment

# Security (REQUIRED)
JWT_SECRET=your-super-secure-production-secret-key-minimum-32-chars
DEBUG=false

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=WARNING

# Rate Limiting
RATE_LIMIT=1000/minute

# CORS (Adjust for your domains)
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=*

# Database (if applicable)
DATABASE_URL=postgresql://user:password@db:5432/database

# Monitoring (optional)
SENTRY_DSN=https://your-sentry-dsn.sentry.io
```

## 🚨 Common Production Issues & Solutions

### Issue: JWT Authentication Failing
**Symptoms**: 401 errors, "Invalid token" messages
**Solution**: 
- Verify `JWT_SECRET` is set correctly
- Check token expiration times
- Ensure consistent secret across all instances

### Issue: CORS Errors
**Symptoms**: Browser console errors, blocked requests
**Solution**:
- Set specific origins instead of `*`
- Include all necessary headers
- Verify preflight OPTIONS handling

### Issue: Rate Limiting Too Aggressive
**Symptoms**: Legitimate requests being blocked
**Solution**:
- Adjust `RATE_LIMIT` configuration
- Implement user-specific rate limiting
- Consider IP whitelisting for known clients

### Issue: Performance Issues
**Symptoms**: Slow response times, high CPU usage
**Solution**:
- Increase worker processes
- Optimize database queries
- Add caching layer
- Profile application bottlenecks

## 📈 Post-Deployment Monitoring

### Key Metrics to Monitor
- **Response Times**: P95, P99 latencies
- **Error Rates**: 4xx, 5xx error percentages  
- **Throughput**: Requests per second
- **Resource Usage**: CPU, Memory, Disk I/O
- **Database Performance**: Query times, connection pools

### Recommended Monitoring Stack
- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Error Tracking**: Sentry or similar
- **Uptime Monitoring**: Pingdom, UptimeRobot, or DataDog

## ✅ Production Deployment Validation

After deployment, verify:

```bash
# Health check
curl https://your-domain.com/health

# CORS headers
curl -H "Origin: https://your-frontend-domain.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://your-domain.com/api/endpoint

# Rate limiting headers
curl -I https://your-domain.com/api/endpoint

# Security headers
curl -I https://your-domain.com/
```

---

🎉 **Congratulations!** Your ZestAPI application is production-ready when all items are checked off.

For additional support, refer to:
- [Production Guide](PRODUCTION_GUIDE.md)
- [LLM Guide](LLM_GUIDE.md) 
- [Framework Documentation](README.md)
