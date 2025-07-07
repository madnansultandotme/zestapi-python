#!/usr/bin/env python3
"""
Build script for ZestAPI package.
"""
import subprocess
import sys
import shutil
from pathlib import Path


def clean_build():
    """Clean previous build artifacts."""
    print("🧹 Cleaning build artifacts...")

    # Remove build directories
    for dir_name in ["build", "dist", "*.egg-info"]:
        for path in Path(".").glob(dir_name):
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"  Removed {path}")
                else:
                    path.unlink()
                    print(f"  Removed {path}")


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("❌ Tests failed!")
        print(result.stdout)
        print(result.stderr)
        return False

    print("✅ All tests passed!")
    return True


def build_package():
    """Build the package."""
    print("📦 Building package...")

    result = subprocess.run(
        [sys.executable, "-m", "build"], capture_output=True, text=True
    )

    if result.returncode != 0:
        print("❌ Build failed!")
        print(result.stdout)
        print(result.stderr)
        return False

    print("✅ Package built successfully!")
    return True


def main():
    """Main build process."""
    print("🚀 ZestAPI Build Process")
    print("=" * 50)

    # Clean previous builds
    clean_build()

    # Run tests
    if not run_tests():
        sys.exit(1)

    # Build package
    if not build_package():
        sys.exit(1)

    print("\n🎉 Build completed successfully!")
    print("📋 Next steps:")
    print("  - Check dist/ directory for built packages")
    print("  - Run 'twine check dist/*' to validate")
    print("  - Run 'twine upload dist/*' to publish")


if __name__ == "__main__":
    main()
