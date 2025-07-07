#!/usr/bin/env python3
"""
Quick deployment script for ZestAPI to GitHub and PyPI.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        # Fix Windows HOME variable issue for Git commands
        if command.startswith('git'):
            # Set environment variable for the subprocess
            env = os.environ.copy()
            env['HOME'] = '/c/Users/adnan'
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, env=env)
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False


def check_git_status():
    """Check if there are uncommitted changes."""
    # Fix Windows HOME variable issue
    env = os.environ.copy()
    env['HOME'] = '/c/Users/adnan'
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True, env=env)
    if result.stdout.strip():
        print("⚠️  Warning: You have uncommitted changes:")
        print(result.stdout)
        response = input("Continue anyway? (y/N): ")
        return response.lower() == 'y'
    return True


def setup_git_config():
    """Setup Git configuration with user identity."""
    print("🔧 Setting up Git configuration...")
    
    # Set Git user name and email
    if not run_command('git config user.name "madnansultandotme"', "Setting Git username"):
        return False
    
    if not run_command('git config user.email "info.adnansultan@gmail.com"', "Setting Git email"):
        return False
    
    print("✅ Git configuration completed")
    return True


def deploy_to_github():
    """Deploy to GitHub."""
    print("\n🐙 GitHub Deployment")
    print("=" * 40)
    
    # Setup Git configuration first
    if not setup_git_config():
        return False
    
    # Check git status
    if not check_git_status():
        return False
    
    # Add and commit any remaining changes
    if not run_command("git add .", "Adding files"):
        return False
    
    # Check if there's anything to commit
    env = os.environ.copy()
    env['HOME'] = '/c/Users/adnan'
    result = subprocess.run("git diff --cached --quiet", shell=True, env=env)
    if result.returncode != 0:
        commit_msg = input("Enter commit message (or press Enter for 'Update project'): ")
        if not commit_msg:
            commit_msg = "Update project"
        
        if not run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
            return False
    
    # Push to GitHub
    if not run_command("git push origin main", "Pushing to GitHub"):
        return False
    
    return True


def build_and_check_package():
    """Build and validate the package."""
    print("\n📦 Package Building")
    print("=" * 40)
    
    # Clean previous builds
    if not run_command("make clean", "Cleaning previous builds"):
        return False
    
    # Run tests
    if not run_command("make test", "Running tests"):
        return False
    
    # Build package
    if not run_command("python scripts/build.py", "Building package"):
        return False
    
    return True


def create_release_tag():
    """Create a release tag."""
    print("\n🏷️  Release Tagging")
    print("=" * 40)
    
    # Get current version
    try:
        with open("zestapi/__init__.py", "r") as f:
            content = f.read()
            version_line = [line for line in content.split('\n') if '__version__' in line][0]
            version = version_line.split('"')[1]
    except:
        print("❌ Could not determine version from __init__.py")
        return False
    
    print(f"📋 Current version: {version}")
    
    # Check if tag already exists
    result = subprocess.run(f"git tag -l v{version}", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print(f"⚠️  Tag v{version} already exists")
        response = input("Create new tag anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Create tag
    if not run_command(f"git tag v{version}", f"Creating tag v{version}"):
        return False
    
    # Push tag
    if not run_command(f"git push origin v{version}", f"Pushing tag v{version}"):
        return False
    
    print(f"✅ Tag v{version} created and pushed")
    print(f"🚀 GitHub Actions will automatically publish to PyPI")
    
    return True


def main():
    """Main deployment process."""
    print("🚀 ZestAPI Deployment Script")
    print("=" * 50)
    
    if not Path("zestapi").exists():
        print("❌ Error: Run this script from the ZestAPI project root directory")
        sys.exit(1)
    
    print("This script will:")
    print("1. Deploy code to GitHub")
    print("2. Build and validate package")
    print("3. Create release tag (triggers auto-publish to PyPI)")
    print()
    
    response = input("Continue with deployment? (y/N): ")
    if response.lower() != 'y':
        print("❌ Deployment cancelled")
        sys.exit(0)
    
    # Step 1: Deploy to GitHub
    if not deploy_to_github():
        print("❌ GitHub deployment failed")
        sys.exit(1)
    
    # Step 2: Build and check package
    if not build_and_check_package():
        print("❌ Package building failed")
        sys.exit(1)
    
    # Step 3: Create release tag
    print("\n🎯 Ready to create release tag")
    print("This will trigger automatic PyPI publishing via GitHub Actions")
    response = input("Create release tag? (y/N): ")
    
    if response.lower() == 'y':
        if not create_release_tag():
            print("❌ Release tagging failed")
            sys.exit(1)
        
        print("\n🎉 Deployment completed successfully!")
        print("📋 Next steps:")
        print("  1. Check GitHub Actions workflow")
        print("  2. Verify PyPI publication")
        print("  3. Test: pip install zestapi")
        print("  4. Create GitHub release with changelog")
    else:
        print("\n✅ Code deployed to GitHub successfully!")
        print("📋 To publish to PyPI later:")
        print("  1. Run: git tag v<version>")
        print("  2. Run: git push origin v<version>")

if __name__ == "__main__":
    main()
