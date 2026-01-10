#!/bin/bash

# Pixel Art Converter - GitHub Setup Script
# This script helps you push the project to GitHub

set -e

echo "=========================================="
echo "Pixel Art Converter - GitHub Setup"
echo "=========================================="
echo ""

# Check if git is configured
if [ -z "$(git config user.email)" ]; then
    echo "Please configure your Git user:"
    read -p "Enter your email: " email
    read -p "Enter your name: " name
    git config user.email "$email"
    git config user.name "$name"
fi

# Check for GitHub remote
if git remote | grep -q "origin"; then
    echo "Remote 'origin' already exists."
    read -p "Do you want to update it? (y/n): " update_remote
    if [ "$update_remote" = "y" ]; then
        read -p "Enter your GitHub repository URL: " repo_url
        git remote set-url origin "$repo_url"
    fi
else
    read -p "Enter your GitHub repository URL: " repo_url
    git remote add origin "$repo_url"
fi

echo ""
echo "Pushing main branch to GitHub..."
git push -u origin main

echo ""
echo "Pushing feature/logging branch to GitHub..."
git push -u origin feature/logging

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Your repository has been pushed to GitHub."
echo ""
echo "Next steps:"
echo "1. Go to your GitHub repository"
echo "2. Check the Actions tab to see CI/CD running"
echo "3. Create a Pull Request from feature/logging to main"
echo ""
echo "Branches pushed:"
echo "  - main (5 commits)"
echo "  - feature/logging (1 additional commit)"
echo ""
