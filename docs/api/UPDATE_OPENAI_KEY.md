# Updating OpenAI API Key in GCP Deployment

## Quick Update Methods

### Method 1: Using the Update Script (Recommended)
```bash
# Run the update script with your new API key
./update-openai-key-gcp.sh sk-proj-YOUR_NEW_API_KEY_HERE
```

### Method 2: Manual kubectl Commands

#### Step 1: Connect to GKE Cluster
```bash
# Set project
gcloud config set project garak-shield

# Get cluster credentials
gcloud container clusters get-credentials nemo-guardrails-production --region us-central1
```

#### Step 2: Update the Secret
```bash
# Delete old secret (if exists)
kubectl delete secret openai-api-key -n default --ignore-not-found=true

# Create new secret with your API key
kubectl create secret generic openai-api-key \
  --from-literal=api-key="sk-proj-YOUR_NEW_API_KEY_HERE" \
  -n default
```

#### Step 3: Restart Deployment
```bash
# Restart the deployment to pick up new secret
kubectl rollout restart deployment/nemo-guardrails-secure -n default

# Watch the rollout status
kubectl rollout status deployment/nemo-guardrails-secure -n default
```

#### Step 4: Verify
```bash
# Check pods are running
kubectl get pods -n default

# Check logs for any errors
kubectl logs -f deployment/nemo-guardrails-secure -n default --tail=50
```

### Method 3: Using Google Secret Manager (If Configured)

```bash
# Update secret in Secret Manager
echo -n "sk-proj-YOUR_NEW_API_KEY_HERE" | gcloud secrets versions add openai-api-key --data-file=-

# Restart deployment to pick up new secret
kubectl rollout restart deployment/nemo-guardrails-secure -n default
```

## Testing After Update

### 1. Test Health Endpoint
```bash
curl https://api.garaksecurity.com/health
```

### 2. Test Chat Completion
```bash
curl -X POST https://api.garaksecurity.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello, how are you?"}]}'
```

## Troubleshooting

### Check Current Configuration
```bash
# View current environment variables (won't show secret values)
kubectl describe deployment nemo-guardrails-secure -n default | grep -A 10 "Environment"

# Check if secret exists
kubectl get secrets -n default | grep openai
```

### View Logs
```bash
# View recent logs
kubectl logs deployment/nemo-guardrails-secure -n default --tail=100

# Stream logs
kubectl logs -f deployment/nemo-guardrails-secure -n default
```

### Common Issues

1. **"Invalid API key" errors in logs**
   - Verify the API key format (should start with `sk-proj-`)
   - Check if the key is active in OpenAI dashboard
   - Ensure no extra spaces or quotes in the secret

2. **Pods not restarting**
   - Force delete pods: `kubectl delete pods -l app=nemo-guardrails-secure -n default`
   - They will automatically recreate with new configuration

3. **Still getting internal server errors**
   - Check if the API key has proper permissions
   - Verify the model access (GPT-4, GPT-3.5-turbo)
   - Check quota/rate limits on OpenAI account

## Security Notes

- Never commit API keys to git
- Use secrets management (Kubernetes Secrets or Google Secret Manager)
- Rotate keys regularly
- Monitor API usage in OpenAI dashboard

## Quick Verification Commands

```bash
# All-in-one verification
echo "=== Checking Deployment Status ===" && \
kubectl get pods -n default -l app=nemo-guardrails-secure && \
echo -e "\n=== Checking Service Health ===" && \
curl -s https://api.garaksecurity.com/health | python3 -m json.tool && \
echo -e "\n=== Testing Chat Completion ===" && \
curl -s -X POST https://api.garaksecurity.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Say hello"}]}' | python3 -m json.tool | head -20
```