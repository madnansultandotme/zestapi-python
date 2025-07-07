#!/usr/bin/env python3
"""
Development setup script for ZestAPI.
"""
import subprocess
import sys
import os
from pathlib import Path


def install_dev_dependencies():
    """Install development dependencies."""
    print("📦 Installing development dependencies...")

    dev_packages = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "httpx>=0.25.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.5.0",
        "build>=0.10.0",
        "twine>=4.0.0",
        "pre-commit>=3.0.0",
    ]

    for package in dev_packages:
        print(f"  Installing {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"❌ Failed to install {package}")
            print(result.stderr)
            return False

    print("✅ Development dependencies installed!")
    return True


def setup_pre_commit():
    """Setup pre-commit hooks."""
    print("🔧 Setting up pre-commit hooks...")

    # Create .pre-commit-config.yaml if it doesn't exist
    pre_commit_config = Path(".pre-commit-config.yaml")
    if not pre_commit_config.exists():
        config_content = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
      
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
      
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]
"""
        with open(pre_commit_config, "w") as f:
            f.write(config_content.strip())
        print("  Created .pre-commit-config.yaml")

    # Install pre-commit hooks
    result = subprocess.run(["pre-commit", "install"], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Failed to install pre-commit hooks")
        print(result.stderr)
        return False

    print("✅ Pre-commit hooks installed!")
    return True


def create_dev_env():
    """Create development environment file."""
    print("📝 Creating development environment file...")

    env_file = Path(".env.dev")
    if not env_file.exists():
        env_content = """
# ZestAPI Development Configuration
JWT_SECRET=dev-secret-key-not-for-production
DEBUG=true
LOG_LEVEL=DEBUG
RATE_LIMIT=10000/minute
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
HOST=127.0.0.1
PORT=8000
RELOAD=true
"""
        with open(env_file, "w") as f:
            f.write(env_content.strip())
        print("  Created .env.dev file")

    print("✅ Development environment configured!")
    return True


def main():
    """Main development setup process."""
    print("🛠️  ZestAPI Development Setup")
    print("=" * 50)

    # Install dev dependencies
    if not install_dev_dependencies():
        sys.exit(1)

    # Setup pre-commit
    if not setup_pre_commit():
        print("⚠️  Pre-commit setup failed, continuing...")

    # Create dev environment
    if not create_dev_env():
        sys.exit(1)

    print("\n🎉 Development environment setup completed!")
    print("📋 Next steps:")
    print("  - Run 'python -m pytest tests/' to run tests")
    print("  - Run 'python scripts/build.py' to build package")
    print("  - Use '.env.dev' for development configuration")
    print("  - Pre-commit hooks will run automatically on commits")


if __name__ == "__main__":
    main()
