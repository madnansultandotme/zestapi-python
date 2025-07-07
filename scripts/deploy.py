#!/usr/bin/env python3
"""
Quick deployment script for ZestAPI.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ {description} failed!")
        print(f"Error: {result.stderr}")
        return False
    
    print(f"✅ {description} completed!")
    if result.stdout.strip():
        print(f"Output: {result.stdout.strip()}")
    return True


def check_git_status():
    """Check git status and repository setup."""
    print("🔍 Checking git status...")
    
    # Check if git is initialized
    if not Path(".git").exists():
        print("📝 Initializing git repository...")
        if not run_command("git init", "Git initialization"):
            return False
    
    # Check if remote origin exists
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    if "origin" not in result.stdout:
        print("🔗 Adding GitHub remote...")
        remote_url = "https://github.com/madnansultandotme/zestapi-python.git"
        if not run_command(f"git remote add origin {remote_url}", "Adding remote origin"):
            return False
    
    return True


def pre_deployment_checks():
    """Run pre-deployment quality checks."""
    print("🧪 Running pre-deployment checks...")
    
    checks = [
        ("python -m pytest tests/ -v", "Running test suite"),
        ("python scripts/build.py", "Building and validating package"),
    ]
    
    for command, description in checks:
        if not run_command(command, description):
            return False
    
    return True


def github_deployment():
    """Deploy to GitHub."""
    print("\n🐙 GitHub Deployment")
    print("=" * 50)
    
    # Check git status
    if not check_git_status():
        return False
    
    # Add all files
    if not run_command("git add .", "Adding all files to git"):
        return False
    
    # Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("📝 No changes to commit")
    else:
        # Commit changes
        commit_message = "Initial release: ZestAPI Python framework v1.0.0"
        if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
            return False
    
    # Set main branch
    if not run_command("git branch -M main", "Setting main branch"):
        return False
    
    # Push to GitHub
    if not run_command("git push -u origin main", "Pushing to GitHub"):
        return False
    
    return True


def pypi_deployment():
    """Deploy to PyPI."""
    print("\n📦 PyPI Deployment")
    print("=" * 50)
    
    # Check if twine is installed
    result = subprocess.run("twine --version", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("📥 Installing twine...")
        if not run_command("pip install twine", "Installing twine"):
            return False
    
    # Check if dist directory exists and has files
    dist_path = Path("dist")
    if not dist_path.exists() or not list(dist_path.glob("*")):
        print("📦 Building package...")
        if not run_command("python scripts/build.py", "Building package"):
            return False
    
    # Validate package
    if not run_command("twine check dist/*", "Validating package"):
        return False
    
    # Upload to PyPI
    print("\n🚀 Ready to upload to PyPI!")
    print("⚠️  This will publish your package publicly to PyPI.")
    
    response = input("Continue with PyPI upload? (y/N): ")
    if response.lower() != 'y':
        print("❌ PyPI upload cancelled.")
        return False
    
    if not run_command("twine upload dist/*", "Uploading to PyPI"):
        return False
    
    return True


def create_release_tag():
    """Create a release tag."""
    print("\n🏷️  Creating Release Tag")
    print("=" * 50)
    
    version = "v1.0.0"  # You can make this configurable
    
    # Create tag
    if not run_command(f"git tag {version}", f"Creating tag {version}"):
        return False
    
    # Push tag
    if not run_command(f"git push origin {version}", f"Pushing tag {version}"):
        return False
    
    print(f"✅ Release tag {version} created and pushed!")
    print("🤖 This should trigger GitHub Actions for automated PyPI publishing.")
    
    return True


def main():
    """Main deployment process."""
    print("🚀 ZestAPI Deployment Script")
    print("=" * 50)
    print("This script will help you deploy ZestAPI to GitHub and PyPI.")
    print()
    
    # Pre-deployment checks
    print("1️⃣  Running pre-deployment checks...")
    if not pre_deployment_checks():
        print("❌ Pre-deployment checks failed. Please fix issues and try again.")
        sys.exit(1)
    
    print("\n✅ Pre-deployment checks passed!")
    
    # Choose deployment method
    print("\n📋 Deployment Options:")
    print("1. GitHub only")
    print("2. GitHub + Manual PyPI")
    print("3. GitHub + Automated PyPI (via GitHub Actions)")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            # GitHub only
            if github_deployment():
                print("\n🎉 GitHub deployment completed successfully!")
                print("📋 Next steps:")
                print("  - Visit https://github.com/madnansultandotme/zestapi-python")
                print("  - Configure repository settings")
                print("  - Set up PyPI API token in GitHub Secrets")
            break
            
        elif choice == "2":
            # GitHub + Manual PyPI
            if github_deployment() and pypi_deployment():
                print("\n🎉 Full deployment completed successfully!")
                print("📋 Your package is now available:")
                print("  - GitHub: https://github.com/madnansultandotme/zestapi-python")
                print("  - PyPI: https://pypi.org/project/zestapi/")
                print("  - Install: pip install zestapi")
            break
            
        elif choice == "3":
            # GitHub + Automated PyPI
            if github_deployment():
                print("\n⚠️  For automated PyPI publishing, you need to:")
                print("  1. Set up PyPI API token in GitHub repository secrets")
                print("  2. Create a release tag to trigger publishing")
                print()
                
                response = input("Create release tag now? (y/N): ")
                if response.lower() == 'y':
                    create_release_tag()
                
                print("\n🎉 GitHub deployment completed!")
                print("📋 Next steps:")
                print("  - Configure PyPI_API_TOKEN in GitHub Secrets")
                print("  - GitHub Actions will handle PyPI publishing")
            break
            
        elif choice == "4":
            print("👋 Deployment cancelled.")
            sys.exit(0)
            
        else:
            print("❌ Invalid choice. Please select 1-4.")


if __name__ == "__main__":
    main()
