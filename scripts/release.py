#!/usr/bin/env python3
"""
Release preparation script for ZestAPI.
"""
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime


def get_current_version():
    """Get current version from __init__.py."""
    init_file = Path("zestapi/__init__.py")
    content = init_file.read_text()

    version_match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if version_match:
        return version_match.group(1)

    raise ValueError("Could not find version in __init__.py")


def update_version(new_version):
    """Update version in relevant files."""
    print(f"📝 Updating version to {new_version}...")

    # Update __init__.py
    init_file = Path("zestapi/__init__.py")
    content = init_file.read_text()
    content = re.sub(
        r'__version__ = ["\'][^"\']+["\']', f'__version__ = "{new_version}"', content
    )
    init_file.write_text(content)
    print("  Updated zestapi/__init__.py")

    # Update pyproject.toml
    pyproject_file = Path("pyproject.toml")
    content = pyproject_file.read_text()
    content = re.sub(
        r'version = ["\'][^"\']+["\']', f'version = "{new_version}"', content
    )
    pyproject_file.write_text(content)
    print("  Updated pyproject.toml")


def update_changelog(version):
    """Update CHANGELOG.md with new version."""
    print("📋 Updating CHANGELOG.md...")

    changelog_file = Path("CHANGELOG.md")
    content = changelog_file.read_text()

    # Add new version entry at the top
    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"""
## [{version}] - {today}

### Added
- 

### Changed
- 

### Fixed
- 

"""

    # Insert after the first heading
    lines = content.split("\n")
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith("##"):
            insert_index = i
            break

    lines.insert(insert_index, new_entry.strip())
    changelog_file.write_text("\n".join(lines))
    print(f"  Added entry for version {version}")


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])

    if result.returncode != 0:
        print("❌ Tests failed! Fix tests before releasing.")
        return False

    print("✅ All tests passed!")
    return True


def main():
    """Main release preparation process."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/release.py <new_version>")
        print("Example: python scripts/release.py 1.1.0")
        sys.exit(1)

    new_version = sys.argv[1]

    # Validate version format
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print("❌ Invalid version format. Use semantic versioning (e.g., 1.1.0)")
        sys.exit(1)

    current_version = get_current_version()

    print("🚀 ZestAPI Release Preparation")
    print("=" * 50)
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    print()

    # Confirm with user
    response = input("Continue with release preparation? (y/N): ")
    if response.lower() != "y":
        print("❌ Release preparation cancelled.")
        sys.exit(0)

    # Run tests
    if not run_tests():
        sys.exit(1)

    # Update version
    update_version(new_version)

    # Update changelog
    update_changelog(new_version)

    print("\n🎉 Release preparation completed!")
    print("📋 Next steps:")
    print("  1. Review and edit CHANGELOG.md")
    print(
        "  2. Commit changes: git add -A && git commit -m 'Prepare release v{}'".format(
            new_version
        )
    )
    print("  3. Create tag: git tag v{}".format(new_version))
    print("  4. Push: git push && git push --tags")
    print("  5. Run 'python scripts/build.py' to build package")
    print("  6. Upload to PyPI: twine upload dist/*")


if __name__ == "__main__":
    main()
