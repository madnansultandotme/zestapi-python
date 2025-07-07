# Changelog

All notable changes to ZestAPI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-07

### Added
- Initial release of ZestAPI Python framework
- ASGI 3.0 compatibility with Starlette backend
- Auto-discovery system for routes and plugins
- Built-in JWT authentication with python-jose
- Rate limiting middleware with configurable strategies
- CORS support with security defaults
- Comprehensive error handling with request tracking
- Request/response logging middleware
- CLI tools for project scaffolding and management
- WebSocket support for real-time applications
- Pydantic v2 integration for data validation (modern patterns)
- orjson for high-performance JSON serialization
- Environment-based configuration with .env support
- Plugin system for modular functionality
- Production-ready middleware stack
- Docker and Kubernetes deployment examples
- Comprehensive documentation and examples

### Changed
- **Pydantic V2 Migration**: Updated from deprecated `@validator` to modern `@field_validator`
- **Settings Configuration**: Migrated from `Config` class to `model_config` with `SettingsConfigDict`
- **Model Methods**: Updated from `.dict()` to `.model_dump()` for better performance
- **Type Safety**: Enhanced type hints and validation with Pydantic V2 improvements

### Features
- **Auto-Discovery**: Routes automatically discovered from `app/routes/` directory
- **Security**: JWT authentication, rate limiting, CORS, input validation
- **Performance**: ASGI 3.0, orjson serialization, async/await throughout
- **Developer Experience**: CLI tools, hot reload, comprehensive error messages
- **Production Ready**: Logging, monitoring, health checks, environment config
- **LLM Friendly**: AI-assistant optimized documentation and patterns

### CLI Commands
- `zest init` - Initialize new ZestAPI project
- `zest generate route <name>` - Generate route file with boilerplate
- `zest generate plugin <name>` - Generate plugin file with boilerplate
- `zest route-map` - Display all discovered routes
- `zest version` - Show framework version

### Security
- JWT token creation and validation
- Configurable CORS policies
- Rate limiting with multiple strategies (per-minute, per-hour, etc.)
- Secure defaults for production deployment
- Input validation with Pydantic
- Error sanitization in production mode

### Documentation
- Complete framework documentation
- LLM-friendly quick reference guide
- Production deployment guide with Docker/Kubernetes
- Step-by-step production checklist
- Multiple example applications
- Contributing guidelines

### Examples
- Basic API with CRUD operations
- Production-ready deployment configuration
- Authentication and JWT implementation
- WebSocket chat application
- Microservice patterns
- Plugin system demonstrations

### Dependencies
- `starlette>=0.46.0` - ASGI framework foundation
- `uvicorn[standard]>=0.30.0` - ASGI server
- `orjson>=3.10.0` - High-performance JSON serialization
- `python-jose[cryptography]>=3.3.0` - JWT implementation
- `pydantic>=2.5.0` - Data validation
- `pydantic-settings>=2.0.0` - Settings management
- `python-multipart>=0.0.6` - Form data parsing
- `python-dotenv>=1.0.0` - Environment variable loading

## [Unreleased]

### Planned
- OAuth2 integration
- Enhanced plugin ecosystem
- GraphQL support
- Advanced monitoring and metrics
- Database integration patterns
- Message queue support
- Caching middleware
- API versioning utilities

---

For a complete list of changes, see the [commit history](https://github.com/madnansultandotme/zestapi-python/commits/main).
