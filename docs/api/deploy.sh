#!/bin/bash

# Manual deployment script for documentation
# Use this for deploying to gh-pages branch manually

set -e

echo "Building documentation..."
sphinx-build -b html . _build/html

echo "Adding .nojekyll file..."
touch _build/html/.nojekyll

echo "Copying CNAME file..."
cp CNAME _build/html/

echo "Preparing for deployment..."
cd _build/html

# Initialize git repo in build directory
git init
git add -A
git commit -m "Deploy documentation to GitHub Pages"

# Push to gh-pages branch
echo "Pushing to gh-pages branch..."
git push -f git@github.com:YOUR_GITHUB_USERNAME/garak-guardrails-platform.git main:gh-pages

echo "Documentation deployed successfully!"
echo "Visit https://docs.garaksecurity.com once DNS is configured"
echo ""
echo "DNS Configuration Required:"
echo "1. Add CNAME record: docs.garaksecurity.com -> YOUR_GITHUB_USERNAME.github.io"
echo "2. Or add A records pointing to GitHub Pages IPs:"
echo "   - 185.199.108.153"
echo "   - 185.199.109.153"
echo "   - 185.199.110.153"
echo "   - 185.199.111.153"