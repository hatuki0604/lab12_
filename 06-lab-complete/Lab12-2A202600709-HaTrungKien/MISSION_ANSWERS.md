# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production
### Exercise 1.1: Anti-patterns found
1. Hardcoded API Keys / Secrets
2. Fixed Ports (not using ENV)
3. Running with Debug Mode enabled
4. Missing Health Check endpoints
5. No Graceful Shutdown handling

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcoded | Environment Variables | Security, flexibility between environments |
| Health check | None | `/health`, `/ready` | Orchestrators (Docker, K8s, Railway) need to know when app is alive/ready |
| Logging | `print()` | Structured JSON | Centralized log aggregation, easy parsing and monitoring |
| Shutdown | Abrupt | Graceful (signal handling) | Prevent dropping active requests and corrupting data |

## Part 2: Docker
### Exercise 2.1: Dockerfile questions
1. Base image: `python:3.11-slim`
2. Working directory: `/app`
3. Why COPY requirements.txt first?: To leverage Docker layer caching so we don't reinstall dependencies if only source code changes.
4. CMD vs ENTRYPOINT: CMD is the default command, ENTRYPOINT is the executable. CMD can be easily overridden.

### Exercise 2.3: Image size comparison
- Develop: ~900 MB
- Production (Multi-stage): ~250 MB
- Difference: ~70% smaller

## Part 4: API Security
### Exercise 4.4: Cost guard implementation
Dùng Redis `incrbyfloat` để cộng dồn chi phí theo tháng (key: `budget:{user_id}:{YYYY-MM}`). Thiết lập expiration (TTL) cho key này là 32 ngày để tự động reset vào tháng mới.

## Part 5: Scaling & Reliability
### Exercise 5.1-5.5: Implementation notes
- Health Check: `/health` trả về 200 OK. `/ready` kiểm tra ping Redis.
- Graceful Shutdown: `signal.signal(signal.SIGTERM, _handle_signal)`
- Stateless Design: Token usage and limits lưu ở Redis thay vì in-memory dict.
