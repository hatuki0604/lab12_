# Deployment Information

## Public URL
https://<your-project-name>.up.railway.app

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://<your-project-name>.up.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X GET https://<your-project-name>.up.railway.app/api/seed-cafes \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json"
# Expected: {"seed_cafes": [...]}
```

## Environment Variables Set
- AGENT_API_KEY
- REDIS_URL
- RATE_LIMIT_PER_MINUTE
- MONTHLY_BUDGET_USD

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
