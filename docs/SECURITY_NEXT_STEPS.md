# 🚨 Security Fix Plan - Exposed Secrets in Git History

**Created**: August 8, 2025  
**Priority**: P0 - CRITICAL  
**Time Required**: 2-3 hours  
**Impact**: Git history rewrite required

## 🔴 CRITICAL EXPOSED SECRETS FOUND

| Secret Type | Value Pattern | Commits | Risk Level |
|------------|--------------|---------|------------|
| OpenAI API Key #1 | `sk-WVpThD4kQt...` | 5 commits | CRITICAL |
| OpenAI API Key #2 | `[REDACTED_API_KEY]| 2 commits | CRITICAL |
| Redis Password | `redis123` | 1 commit | HIGH |
| Grafana Password | `admin123` | 3 commits | HIGH |

---

## 📋 IMMEDIATE ACTION PLAN

### **Step 1: REVOKE COMPROMISED KEYS (Do Now - 15 min)**

#### 1.1 Revoke OpenAI API Keys
```bash
# Go to OpenAI Dashboard immediately
# https://platform.openai.com/api-keys
# 
# Revoke these specific keys:
# 1. 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
# 2. [REDACTED_API_KEY]

# Generate new API key and save to .env (never commit!)
echo "OPENAI_API_KEY=your-new-key-here" >> .env
```

#### 1.2 Generate Secure Passwords
```bash
# Generate cryptographically secure passwords
export REDIS_PASSWORD=$(openssl rand -base64 32)
export GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 32)

# Save to .env file (already in .gitignore)
cat >> .env << EOF
REDIS_PASSWORD=$REDIS_PASSWORD
GRAFANA_ADMIN_PASSWORD=$GRAFANA_ADMIN_PASSWORD
EOF

# Display for manual updates if needed
echo "New Redis Password: $REDIS_PASSWORD"
echo "New Grafana Password: $GRAFANA_ADMIN_PASSWORD"
```

---

### **Step 2: CLEAN GIT HISTORY (30-60 min)**

#### Option A: Using BFG Repo-Cleaner (RECOMMENDED - Faster & Safer)

```bash
# 1. Install BFG
# macOS
brew install bfg

# Linux/Windows - Download from https://rtyley.github.io/bfg-repo-cleaner/
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar
alias bfg='java -jar bfg-1.14.0.jar'

# 2. Clone a fresh copy (for safety)
git clone --mirror https://github.com/your-org/NeMo-Guardrails.git NeMo-Guardrails-mirror
cd NeMo-Guardrails-mirror

# 3. Create file with secrets to remove
cat > ../secrets-to-remove.txt << 'EOF'
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
[REDACTED_API_KEY]
redis123
admin123
EOF

# 4. Run BFG to clean secrets
bfg --replace-text ../secrets-to-remove.txt

# 5. Clean up git history
git reflog expire --expire=now --all && git gc --prune=now --aggressive

# 6. Push cleaned history (WARNING: This rewrites history!)
git push --force --all
git push --force --tags
```

#### Option B: Using Native Git (More Complex)

```bash
# 1. Create backup first
git clone . ../NeMo-Guardrails-backup

# 2. Create cleaning script
cat > clean-secrets.sh << 'EOF'
#!/bin/bash
set -e

echo "🧹 Cleaning secrets from git history..."

# Remove files with hardcoded secrets
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch \
   deploy_gcp_production_security.sh \
   k8s-deployments/working-with-buildtools.yaml \
   k8s-deployments/simple-nemo-deployment.yaml 2>/dev/null || true' \
  --prune-empty --tag-name-filter cat -- --all

# Replace secret strings in all files
git filter-branch --force --tree-filter '
  find . -type f -exec sed -i.bak \
    -e "s/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/REDACTED_OPENAI_KEY/g" \
    -e "s/[REDACTED_API_KEY]/REDACTED_OPENAI_KEY/g" \
    -e "s/redis123/REDIS_PASSWORD_PLACEHOLDER/g" \
    -e "s/admin123/GRAFANA_PASSWORD_PLACEHOLDER/g" {} + 2>/dev/null || true
  find . -name "*.bak" -delete 2>/dev/null || true
' -- --all

echo "✅ Secrets cleaned from history"
EOF

chmod +x clean-secrets.sh
./clean-secrets.sh

# 3. Clean up refs and garbage collect
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Force push (WARNING: Breaks existing clones!)
git push origin --force --all
git push origin --force --tags
```

---

### **Step 3: UPDATE LIVE DEPLOYMENTS (30 min)**

#### 3.1 Update Kubernetes Secrets
```bash
# Delete compromised secrets
kubectl delete secret openai-secret redis-auth grafana-admin --ignore-not-found=true

# Create new secrets with secure values
kubectl create secret generic openai-secret \
  --from-literal=api-key=$OPENAI_API_KEY

kubectl create secret generic redis-auth \
  --from-literal=password=$REDIS_PASSWORD

kubectl create secret generic grafana-admin \
  --from-literal=password=$GRAFANA_ADMIN_PASSWORD

# Verify secrets created
kubectl get secrets
```

#### 3.2 Update Running Services
```bash
# Update Redis password
kubectl set env deployment/redis REDIS_PASSWORD=$REDIS_PASSWORD

# Update Grafana admin password  
kubectl set env deployment/grafana GF_SECURITY_ADMIN_PASSWORD=$GRAFANA_ADMIN_PASSWORD

# Restart all affected deployments
kubectl rollout restart deployment nemo-guardrails-secure
kubectl rollout restart deployment redis
kubectl rollout restart deployment grafana

# Monitor rollout status
kubectl rollout status deployment/nemo-guardrails-secure
kubectl rollout status deployment/redis
kubectl rollout status deployment/grafana
```

#### 3.3 Verify Services
```bash
# Check pod status
kubectl get pods

# Test API endpoint
curl https://api.garaksecurity.com/health

# Check logs for errors
kubectl logs -l app=nemo-guardrails-secure --tail=100 | grep -i error
```

---

### **Step 4: PREVENT FUTURE EXPOSURE (30 min)**

#### 4.1 Install Pre-commit Hooks
```bash
# Install pre-commit framework
pip install pre-commit detect-secrets

# Create pre-commit configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  # Detect secrets in staged files
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package-lock.json
  
  # Scan for leaked credentials
  - repo: https://github.com/zricethezav/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  # General security checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-case-conflict
      - id: check-merge-conflict
EOF

# Generate baseline for existing secrets (to ignore false positives)
detect-secrets scan --baseline .secrets.baseline

# Install the git hooks
pre-commit install
pre-commit run --all-files
```

#### 4.2 Create Security Documentation
```bash
cat > SECURITY_GUIDELINES.md << 'EOF'
# 🔒 Security Guidelines

## ❌ NEVER Commit

- API keys (OpenAI, AWS, GCP, Azure, etc.)
- Passwords (Database, Redis, Admin panels)
- Private keys or certificates
- Service account JSON files
- .env files
- OAuth tokens
- Webhook URLs with embedded secrets

## ✅ ALWAYS Use

- Environment variables for secrets
- Kubernetes secrets for deployments
- .env files locally (never commit)
- Secret management services:
  - GCP Secret Manager
  - AWS Secrets Manager
  - HashiCorp Vault
  - Azure Key Vault

## 🔍 Before EVERY Commit

1. **Check staged files for secrets:**
   ```bash
   git diff --staged | grep -E "(sk-|api[_-]?key|password|secret|token)"
   ```

2. **Verify no sensitive files:**
   ```bash
   git status | grep -E "(.env|.pem|.key|credentials)"
   ```

3. **Run pre-commit hooks:**
   ```bash
   pre-commit run
   ```

## 🚨 If Secrets Are Exposed

1. **Immediately revoke** the exposed credentials
2. **Generate new** credentials
3. **Clean git history** using BFG or git filter-branch
4. **Force push** cleaned history
5. **Notify team** about the force push
6. **Monitor** for unauthorized usage

## 📋 Secret Management Checklist

- [ ] All API keys in environment variables
- [ ] .env file in .gitignore
- [ ] Pre-commit hooks installed
- [ ] Team trained on security practices
- [ ] Regular secret rotation scheduled
- [ ] Monitoring for exposed secrets enabled
EOF
```

#### 4.3 Add GitHub Secret Scanning
```bash
# Enable in GitHub repository settings:
# 1. Go to Settings → Security → Code security and analysis
# 2. Enable "Secret scanning"
# 3. Enable "Push protection" (blocks commits with secrets)

# Add custom patterns for your organization
cat > .github/secret_scanning.yml << 'EOF'
patterns:
  - name: OpenAI API Key
    pattern: 'sk-[a-zA-Z0-9]{48}'
  - name: OpenAI Project Key
    pattern: 'sk-proj-[a-zA-Z0-9_-]{100,}'
  - name: Generic API Key
    pattern: 'api[_-]?key["\s]*[:=]["\s]*[a-zA-Z0-9_-]{32,}'
  - name: Redis Password
    pattern: 'redis[_-]?password["\s]*[:=]["\s]*[^"\s]+'
EOF
```

---

### **Step 5: AUDIT & MONITOR (Ongoing)**

#### 5.1 Check for Unauthorized Usage
```bash
# Monitor OpenAI usage
echo "Check: https://platform.openai.com/usage"
echo "Look for unusual spikes or unexpected usage"

# Check GCP logs for suspicious activity
gcloud logging read "resource.type=k8s_cluster AND severity>=WARNING" \
  --limit=100 \
  --format="table(timestamp,severity,textPayload)"

# Check for failed authentication attempts
kubectl logs -l app=nemo-guardrails-secure --since=24h | grep -i "auth\|forbidden\|unauthorized"
```

#### 5.2 Set Up Continuous Monitoring
```bash
# Create monitoring script
cat > monitor-secrets.sh << 'EOF'
#!/bin/bash
# Run this script regularly (e.g., via cron or CI/CD)

echo "🔍 Scanning for exposed secrets..."

# Check current branch
git log -p -10 | grep -E "(sk-|password=|api[_-]?key=)" && {
  echo "⚠️ WARNING: Potential secrets found in recent commits!"
  exit 1
}

# Check all branches
for branch in $(git branch -r | grep -v HEAD); do
  git log -p -10 $branch | grep -E "(sk-|password=|api[_-]?key=)" && {
    echo "⚠️ WARNING: Potential secrets found in $branch!"
    exit 1
  }
done

echo "✅ No secrets found in recent history"
EOF

chmod +x monitor-secrets.sh
```

---

## 📊 Execution Timeline

| Time | Priority | Action | Verification |
|------|----------|--------|--------------|
| 0-15 min | P0 | Revoke API keys | Check OpenAI dashboard |
| 15-30 min | P0 | Generate new credentials | Test with curl |
| 30-60 min | P1 | Clean git history | Run `git log` searches |
| 60-90 min | P1 | Update deployments | Check `kubectl get pods` |
| 90-120 min | P2 | Install protections | Run pre-commit test |
| Ongoing | P2 | Monitor & audit | Check logs daily |

---

## ✅ Verification Commands

```bash
# 1. Verify secrets removed from history
echo "Checking for exposed secrets in git history..."
git log --all --full-history -p | grep -E "sk-|redis123|admin123" || echo "✅ Clean"

# 2. Verify new credentials work
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models || echo "❌ API key invalid"

# 3. Test deployed services
curl https://api.garaksecurity.com/health || echo "❌ Service down"

# 4. Verify pre-commit hooks
pre-commit run --all-files || echo "❌ Pre-commit checks failed"

# 5. Final security scan
detect-secrets scan | grep "no secrets detected" || echo "⚠️ Potential secrets found"
```

---

## ⚠️ CRITICAL WARNINGS

### Before Force Push:
1. **Notify all team members** - They will need to re-clone
2. **Backup the repository** - Create a safety copy
3. **Close all PRs** - They will become invalid
4. **Document the change** - Update team wiki/docs
5. **Schedule during low activity** - Minimize disruption

### After Cleanup:
1. **All developers must re-clone** the repository
2. **Update all CI/CD pipelines** with new credentials
3. **Monitor billing** for 30 days for unauthorized usage
4. **Consider rotating** other potentially exposed secrets
5. **Security training** for all team members

### If Repository is Public:
- Consider deleting and recreating as private
- Assume all historical secrets are compromised
- Implement additional access controls
- Enable all GitHub security features

---

## 📞 Escalation Contacts

| Issue | Contact | Action |
|-------|---------|--------|
| OpenAI API abuse | support@openai.com | Report compromised key |
| GCP suspicious activity | GCP Support Console | Open P1 ticket |
| GitHub security | security@github.com | Report exposed secrets |
| Team notification | Team Slack/Email | Send immediate alert |

---

## 🎯 Success Criteria

- [ ] All exposed API keys revoked
- [ ] New secure credentials deployed
- [ ] Git history cleaned of secrets
- [ ] All services running with new credentials
- [ ] Pre-commit hooks preventing future exposure
- [ ] Team notified and trained
- [ ] Monitoring in place
- [ ] No unauthorized usage detected

---

**Document Version**: 1.0  
**Last Updated**: August 8, 2025  
**Next Review**: After completion of all steps  
**Owner**: Security Team / DevOps Team