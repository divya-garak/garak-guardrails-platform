# Documentation Deployment Guide

This guide explains how to deploy the Garak API documentation to https://docs.getgarak.com/.

## Automatic Deployment (GitHub Actions)

The documentation is automatically deployed when changes are pushed to the main branch:

1. **Workflow**: `.github/workflows/deploy-docs.yml` handles the deployment
2. **Triggers**: 
   - Push to `main` or `api-documentation` branches
   - Changes to files in `docs/api/`
   - Manual trigger via GitHub Actions UI

## Manual Deployment

To deploy manually using the provided script:

```bash
cd docs/api
./deploy.sh
```

Note: Update `YOUR_GITHUB_USERNAME` in the script with your actual GitHub username.

## Initial Setup

### 1. Enable GitHub Pages

1. Go to repository Settings → Pages
2. Select "Deploy from a branch"
3. Choose `gh-pages` branch and `/` (root) folder
4. Save the configuration

### 2. Configure DNS

Add one of the following DNS configurations to your domain provider:

**Option A: CNAME Record (Recommended)**
```
Type: CNAME
Name: docs
Value: YOUR_GITHUB_USERNAME.github.io
```

**Option B: A Records**
```
Type: A
Name: docs
Values:
- 185.199.108.153
- 185.199.109.153
- 185.199.110.153
- 185.199.111.153
```

### 3. Verify Custom Domain

1. After DNS propagation (can take up to 24 hours)
2. Go to repository Settings → Pages
3. Enter `docs.getgarak.com` in the custom domain field
4. Wait for DNS check to complete
5. Enable "Enforce HTTPS"

## Building Documentation Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Build documentation
sphinx-build -b html . _build/html

# View locally
open _build/html/index.html
```

## File Structure

```
docs/api/
├── CNAME                   # Custom domain configuration
├── .nojekyll              # Disable Jekyll processing
├── requirements.txt       # Python dependencies
├── deploy.sh             # Manual deployment script
├── conf.py               # Sphinx configuration
├── index.rst             # Documentation index
├── _build/               # Build output (git-ignored)
└── garak-detect-api/     # API documentation content
```

## Troubleshooting

### Documentation not updating
- Check GitHub Actions workflow status
- Verify the gh-pages branch has been created
- Clear browser cache

### Custom domain not working
- Verify DNS records are correctly configured
- Check DNS propagation status: https://dnschecker.org
- Ensure CNAME file exists in the repository
- Verify domain in GitHub Pages settings

### Build failures
- Check Python version (requires 3.9+)
- Verify all dependencies are installed
- Check for RST syntax errors in documentation files

## Alternative Deployment Options

### Netlify
1. Connect repository to Netlify
2. Build command: `cd docs/api && sphinx-build -b html . _build/html`
3. Publish directory: `docs/api/_build/html`
4. Configure custom domain in Netlify settings

### Google Cloud Storage
1. Build documentation locally
2. Upload to GCS bucket named `docs.getgarak.com`
3. Configure bucket for static website hosting
4. Set up Cloud CDN for HTTPS

## Support

For issues with deployment, check:
- GitHub Actions logs for build errors
- GitHub Pages settings for configuration issues
- DNS provider for domain configuration