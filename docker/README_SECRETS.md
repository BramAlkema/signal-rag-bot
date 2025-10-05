# Docker Secrets Configuration

This document explains how to use Docker secrets for secure credential management with the Signal RAG Bot.

## Why Use Docker Secrets?

Docker secrets provide a secure way to store sensitive data without exposing it in:
- Environment variables (visible in `docker inspect`)
- Docker Compose files
- Container logs
- Process listings

## Setup Instructions

### 1. Create Secrets Directory

```bash
mkdir -p secrets
chmod 700 secrets
```

### 2. Create Secret Files

Create text files for each secret:

```bash
# OpenAI API Key
echo "sk-your-actual-api-key-here" > secrets/openai_api_key.txt

# Signal Phone Number (E.164 format)
echo "+31612345678" > secrets/signal_phone_number.txt

# Activation Passphrase (optional)
echo "Your Secret Activation Phrase" > secrets/activation_passphrase.txt
```

### 3. Secure the Files

```bash
chmod 600 secrets/*.txt
```

### 4. Update .gitignore

Ensure secrets directory is excluded from git:

```bash
echo "secrets/" >> .gitignore
```

## Using Secrets with Docker Compose

### Method 1: File-based Secrets (Recommended for Development)

Edit `docker-compose.yml` and uncomment the secrets sections:

```yaml
services:
  signal-rag-bot:
    # ... other config ...
    secrets:
      - openai_api_key
      - signal_phone_number
      - activation_passphrase

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
  signal_phone_number:
    file: ./secrets/signal_phone_number.txt
  activation_passphrase:
    file: ./secrets/activation_passphrase.txt
```

When using secrets, you can remove the corresponding environment variables.

### Method 2: Docker Swarm Secrets (Recommended for Production)

For production deployments using Docker Swarm:

```bash
# Create secrets in Docker Swarm
docker secret create openai_api_key secrets/openai_api_key.txt
docker secret create signal_phone_number secrets/signal_phone_number.txt
docker secret create activation_passphrase secrets/activation_passphrase.txt

# Deploy as a stack
docker stack deploy -c docker-compose.yml signal-rag
```

## How It Works

The entrypoint script (`docker/entrypoint.sh`) automatically checks for secrets at:
- `/run/secrets/openai_api_key`
- `/run/secrets/signal_phone_number`
- `/run/secrets/activation_passphrase`

If found, these secrets override environment variables.

## Fallback to Environment Variables

If Docker secrets are not configured, the bot falls back to environment variables:

```bash
# .env file
OPENAI_API_KEY=sk-your-key-here
SIGNAL_PHONE_NUMBER=+31612345678
ACTIVATION_PASSPHRASE=Your Phrase
```

## Security Best Practices

1. **Never commit secrets to git**
   - Add `secrets/` to `.gitignore`
   - Add `.env` to `.gitignore`

2. **Use appropriate file permissions**
   ```bash
   chmod 700 secrets/          # Directory: owner only
   chmod 600 secrets/*.txt     # Files: owner read/write only
   ```

3. **Rotate secrets regularly**
   - Update secret files
   - Restart container: `docker-compose restart`

4. **Use different secrets for different environments**
   - Development: `secrets/dev/`
   - Staging: `secrets/staging/`
   - Production: Docker Swarm secrets

5. **Audit access**
   - Monitor who has access to secrets
   - Use Docker Swarm for role-based access control

## Example: Full Secrets Setup

```bash
# 1. Create structure
mkdir -p secrets
cd secrets

# 2. Create secret files
echo "sk-proj-abc123..." > openai_api_key.txt
echo "+31612345678" > signal_phone_number.txt
echo "SecureActivationPhrase2024" > activation_passphrase.txt

# 3. Secure files
chmod 600 *.txt
cd ..
chmod 700 secrets

# 4. Update docker-compose.yml (uncomment secrets sections)

# 5. Start with secrets
docker-compose up -d

# 6. Verify secrets are loaded
docker-compose logs | grep "Loaded.*from Docker secret"
```

## Troubleshooting

### Secrets not being loaded

Check the entrypoint logs:
```bash
docker-compose logs signal-rag-bot | grep ENTRYPOINT
```

You should see:
```
[ENTRYPOINT] ✓ Loaded OPENAI_API_KEY from Docker secret
[ENTRYPOINT] ✓ Loaded SIGNAL_PHONE_NUMBER from Docker secret
```

### Permission errors

Ensure correct permissions:
```bash
ls -la secrets/
# Should show: drwx------ (700) for directory
# Should show: -rw------- (600) for files
```

### Secrets not found

Verify secret files exist:
```bash
ls -la secrets/
cat secrets/openai_api_key.txt  # Should show your API key
```

## Cleanup

To remove secrets:

```bash
# Remove secret files
rm -rf secrets/

# Remove Docker secrets (if using Swarm)
docker secret rm openai_api_key signal_phone_number activation_passphrase
```
