#!/bin/bash

# SENTINEL AI - GitHub Deployment Script
# This script prepares your project for GitHub deployment

echo "🚀 SENTINEL AI - GitHub Deployment Setup"
echo "=========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first:"
    echo "   https://git-scm.com/download"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Initialize git repository
if [ -d ".git" ]; then
    echo "⚠️  Git repository already exists"
else
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
fi

echo ""
echo "📝 Adding files to Git..."
git add .
echo "✅ Files staged"

echo ""
echo "💾 Creating initial commit..."
git commit -m "Initial commit: SENTINEL AI v1.0.0 - Real-time Cyber Defense System"
echo "✅ Initial commit created"

echo ""
echo "🌐 Adding remote repository..."
echo ""
echo "Enter your GitHub repository URL:"
echo "Example: https://github.com/YOUR_USERNAME/sentinel-ai.git"
read -p "Repository URL: " repo_url

if [ -z "$repo_url" ]; then
    echo "❌ Repository URL is required"
    exit 1
fi

git remote add origin "$repo_url"
echo "✅ Remote repository configured"

echo ""
echo "🏷️  Renaming branch to main..."
git branch -M main
echo "✅ Branch renamed to main"

echo ""
echo "🚀 Pushing to GitHub..."
git push -u origin main
echo "✅ Code pushed to GitHub!"

echo ""
echo "=========================================="
echo "✅ GitHub Setup Complete!"
echo "=========================================="
echo ""
echo "Your repository is now on GitHub:"
echo "📍 $repo_url"
echo ""
echo "Next steps:"
echo "1. ✅ GitHub Actions will automatically run CI/CD"
echo "2. ✅ Configure GitHub Secrets (if deploying)"
echo "3. ✅ Enable branch protection rules"
echo "4. ✅ Invite collaborators"
echo "5. ✅ Create releases"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Main documentation"
echo "   - QUICKSTART.md - Quick start guide"
echo "   - DEPLOYMENT_READY.md - Production deployment"
echo "   - GITHUB_DEPLOYMENT.md - Detailed GitHub setup"
echo ""
echo "🎉 You're all set! Happy coding!"
