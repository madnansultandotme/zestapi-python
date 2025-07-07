# Contributing to ZestAPI

We welcome contributions to ZestAPI! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.10 or higher
- Git

### Setup Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/madnansultandotme/zestapi-python.git
   cd zestapi-python
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Run Tests**
   ```bash
   pytest test_package.py -v
   ```

## Development Workflow

### Branch Naming
- `feature/description` - For new features
- `bugfix/description` - For bug fixes
- `docs/description` - For documentation changes
- `refactor/description` - For code refactoring

### Commit Messages
Follow conventional commit format:
```
type(scope): description

feat(auth): add JWT token refresh functionality
fix(routes): resolve path parameter parsing issue
docs(readme): update installation instructions
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Code Standards

### Python Code Style
- Follow PEP 8
- Use Black for formatting: `black .`
- Use isort for imports: `isort .`
- Maximum line length: 88 characters

### Type Hints
- All functions should have type hints
- Use `typing` module for complex types
- Example:
  ```python
  from typing import List, Optional, Dict, Any
  
  def process_users(users: List[Dict[str, Any]]) -> Optional[str]:
      # Implementation
      pass
  ```

### Documentation
- All public functions/classes need docstrings
- Use Google-style docstrings:
  ```python
  def create_user(name: str, email: str) -> Dict[str, Any]:
      """Create a new user with validation.
      
      Args:
          name: User's full name
          email: User's email address
          
      Returns:
          Dictionary containing user data
          
      Raises:
          ValueError: If email format is invalid
      """
  ```

## Testing

### Writing Tests
- Tests go in `test_*.py` files
- Use pytest for all tests
- Aim for high test coverage
- Test both success and error cases

### Test Structure
```python
import pytest
from zestapi import ZestAPI

def test_feature_description():
    """Test that feature works correctly."""
    # Arrange
    app = ZestAPI()
    
    # Act
    result = app.some_method()
    
    # Assert
    assert result == expected_value
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=zestapi

# Run specific test file
pytest test_package.py -v
```

## Pull Request Process

### Before Submitting
1. **Code Quality**
   ```bash
   black .                    # Format code
   isort .                   # Sort imports
   pytest test_package.py    # Run tests
   ```

2. **Documentation**
   - Update relevant documentation
   - Add docstrings for new functions
   - Update README if needed

3. **Testing**
   - Add tests for new functionality
   - Ensure all tests pass
   - Test manually if needed

### PR Requirements
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Self-review completed
- [ ] Descriptive commit messages
- [ ] PR description explains changes

### PR Template
Use the provided PR template when submitting:
- Describe the change
- Link related issues
- Include testing information
- Note any breaking changes

## Feature Development

### Adding New Features

1. **Create Issue**
   - Describe the feature
   - Discuss implementation approach
   - Get feedback from maintainers

2. **Implementation**
   - Create feature branch
   - Implement with tests
   - Update documentation
   - Follow code standards

3. **Integration**
   - Ensure backward compatibility
   - Add migration guide if needed
   - Update changelog

### Core Areas

#### Routes and Routing
- File: `zestapi/core/routing.py`
- Auto-discovery system
- Route registration and handling

#### Middleware
- File: `zestapi/core/middleware.py`
- Error handling, logging, security
- Custom middleware support

#### Authentication
- File: `zestapi/core/security.py`
- JWT implementation
- Authentication backends

#### Settings and Configuration
- File: `zestapi/core/settings.py`
- Environment variable handling
- Configuration validation

## Bug Reports

### Reporting Bugs
Use the bug report template with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Code examples

### Fixing Bugs
1. Create issue if not exists
2. Create bugfix branch
3. Write test that reproduces bug
4. Fix the issue
5. Ensure test passes
6. Submit PR

## Documentation

### Types of Documentation
- **API Documentation**: Docstrings in code
- **User Guide**: `docs/` directory
- **Examples**: `examples/` directory
- **README**: Project overview

### Documentation Guidelines
- Write for beginners and experts
- Include code examples
- Keep examples up to date
- Use clear, concise language

## Community

### Communication
- GitHub Issues for bugs and features
- GitHub Discussions for questions
- Code reviews for learning

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn
- Celebrate contributions

## Release Process

### Version Numbering
Follow semantic versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Release Checklist
- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release tag
- [ ] Publish to PyPI

## Getting Help

### Resources
- Documentation: `docs/` directory
- Examples: `examples/` directory
- Issues: GitHub Issues
- Discussions: GitHub Discussions

### Questions
Before asking:
1. Check existing documentation
2. Search closed issues
3. Look at examples
4. Review FAQ

When asking:
- Provide context
- Include code examples
- Specify environment details
- Show what you've tried

---

Thank you for contributing to ZestAPI! 🎉
