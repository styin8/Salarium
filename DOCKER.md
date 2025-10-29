# Docker Architecture Documentation

## Overview

Salarium uses a multi-container Docker setup with:
- **Backend**: FastAPI + Uvicorn on Python 3.12
- **Frontend**: Vue 3 SPA served by Nginx with API reverse proxy
- **Database**: SQLite with host volume persistence

## Container Architecture

```
┌─────────────────────────────────────┐
│         Host Machine                │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Frontend Container         │  │
│  │   (Nginx:Alpine)             │  │
│  │                              │  │
│  │   Port 80 → Host:8080        │  │
│  │                              │  │
│  │   /api/* → backend:8000      │  │
│  │   /*     → /usr/share/.../html│  │
│  └──────────┬───────────────────┘  │
│             │                       │
│             │ salarium-network      │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │   Backend Container          │  │
│  │   (Python:3.12-slim)         │  │
│  │                              │  │
│  │   Port 8000 (internal only)  │  │
│  │   Uvicorn + FastAPI          │  │
│  │                              │  │
│  │   /app/data ← Host:./data/   │  │
│  └──────────────────────────────┘  │
│                                     │
│  ./data/sqlite/salarium.db          │
└─────────────────────────────────────┘
```

## File Structure

```
.
├── backend/
│   ├── Dockerfile              # Backend image definition
│   ├── .dockerignore           # Build exclusions
│   ├── requirements.txt        # Python dependencies
│   ├── config.py               # Environment-aware config
│   └── app/
│       └── main.py             # FastAPI application
├── frontend/
│   ├── Dockerfile              # Frontend multi-stage build
│   ├── .dockerignore           # Build exclusions
│   ├── nginx.conf              # Nginx reverse proxy config
│   └── src/                    # Vue 3 application
├── docker-compose.yml          # Service orchestration
├── .env.example                # Environment template
├── Makefile                    # Convenience commands
└── docker-build.sh             # Build helper script
```

## Backend Container Details

### Dockerfile Stages

**Build Stage:**
- Base: `python:3.12-slim`
- Installs Python packages to user directory
- Uses pip with `--no-cache-dir` for smaller image

**Runtime Stage:**
- Clean Python 3.12-slim base
- Creates non-root user `appuser` (UID 1000)
- Copies installed packages from build stage
- Sets up `/app/data` directory for SQLite

### Security Features
- Runs as non-root user
- Minimal base image (slim)
- No unnecessary packages
- Read-only application code

### Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `UVICORN_HOST` | `0.0.0.0` | Bind address |
| `UVICORN_PORT` | `8000` | Listen port |
| `UVICORN_WORKERS` | `2` | Worker processes |
| `JWT_SECRET` | `super-secret-change-me` | Token signing |
| `JWT_ALGORITHM` | `HS256` | Token algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token lifetime |
| `CORS_ORIGINS` | `*` | Allowed origins |

### Health Check
- Endpoint: `GET /docs`
- Interval: 30 seconds
- Timeout: 10 seconds
- Start period: 5 seconds
- Retries: 3

## Frontend Container Details

### Dockerfile Stages

**Build Stage:**
- Base: `node:20-alpine`
- Runs `npm ci` for reproducible builds
- Executes `npm run build` (Vite)
- Output: `/app/dist`

**Runtime Stage:**
- Base: `nginx:alpine`
- Copies custom `nginx.conf`
- Copies built assets from build stage
- Serves on port 80

### Nginx Configuration

**Static Assets:**
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**API Reverse Proxy:**
```nginx
location /api/ {
    proxy_pass http://backend:8000/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**SPA Routing:**
```nginx
location / {
    try_files $uri $uri/ /index.html;
    add_header Cache-Control "no-cache";
}
```

## Data Persistence

### SQLite Volume Mount

```yaml
volumes:
  - ./data/sqlite:/app/data
```

- **Host Path**: `./data/sqlite`
- **Container Path**: `/app/data`
- **Database File**: `salarium.db`
- **Created**: Automatically on first run
- **Permissions**: 755 (appuser can read/write)

### Backup Strategy

**Manual Backup:**
```bash
cp -r ./data/sqlite ./backup-$(date +%Y%m%d-%H%M%S)
```

**Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/salarium-$(date +%Y%m%d-%H%M%S).tar.gz" ./data/sqlite
find "$BACKUP_DIR" -name "salarium-*.tar.gz" -mtime +30 -delete
```

**Restore:**
```bash
docker compose down
tar -xzf backup-YYYYMMDD-HHMMSS.tar.gz
docker compose up -d
```

## Networking

### Bridge Network
```yaml
networks:
  salarium-network:
    driver: bridge
```

- Isolated network for service communication
- DNS resolution: `backend`, `frontend`
- No direct host access to backend

### Port Mapping
- Frontend: `${FRONTEND_PORT:-8080}:80`
- Backend: Exposed internally only (no host mapping)

## Development Workflow

### Quick Commands

```bash
# Build and start
make up

# View logs
make logs

# Restart services
make restart

# Clean everything
make clean

# Service status
make status
```

### Incremental Development

**Backend changes:**
```bash
docker compose build backend
docker compose up -d backend
```

**Frontend changes:**
```bash
docker compose build frontend
docker compose up -d frontend
```

**Config changes:**
```bash
# Edit .env
docker compose up -d  # Recreates containers with new env
```

### Debugging

**Access backend shell:**
```bash
docker compose exec backend sh
# Inside container:
python -c "import config; print(config.DB_PATH)"
ls -la /app/data/
```

**Access frontend shell:**
```bash
docker compose exec frontend sh
# Inside container:
cat /etc/nginx/conf.d/default.conf
ls -la /usr/share/nginx/html/
```

**Check backend logs:**
```bash
docker compose logs -f backend
```

**Test backend directly:**
```bash
curl http://localhost:8080/api/docs
```

**Inspect network:**
```bash
docker network inspect salarium_salarium-network
```

## Production Considerations

### Security Hardening

1. **Change JWT Secret:**
```env
JWT_SECRET=$(openssl rand -hex 32)
```

2. **Restrict CORS:**
```env
CORS_ORIGINS=https://yourdomain.com
```

3. **Use HTTPS:**
- Add Traefik or Caddy as reverse proxy
- Terminate SSL at proxy layer
- Update nginx.conf to handle X-Forwarded-Proto

4. **Add Resource Limits:**
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### Scaling

**Increase Backend Workers:**
```env
UVICORN_WORKERS=4
```

**Multiple Backend Replicas:**
```yaml
services:
  backend:
    deploy:
      replicas: 3
```

### Monitoring

**Add Health Check Endpoints:**
```python
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**Prometheus Metrics:**
```bash
pip install prometheus-fastapi-instrumentator
```

### Database Migration

**To PostgreSQL:**
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: salarium
      POSTGRES_USER: salarium
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
```

Update backend:
```python
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite://{DB_PATH}")
```

Update compose:
```yaml
backend:
  environment:
    - DATABASE_URL=postgres://salarium:${DB_PASSWORD}@postgres:5432/salarium
  depends_on:
    postgres:
      condition: service_healthy
```

## Troubleshooting

### Common Issues

**Port 8080 in use:**
```bash
# Check what's using the port
lsof -i :8080
# Change port in .env
echo "FRONTEND_PORT=3000" >> .env
```

**Permission denied on data directory:**
```bash
sudo chown -R 1000:1000 ./data/sqlite
chmod 755 ./data/sqlite
```

**Backend unhealthy:**
```bash
# Check logs
docker compose logs backend
# Check if port is listening
docker compose exec backend netstat -tlnp
# Restart with fresh build
docker compose build --no-cache backend
docker compose up -d backend
```

**Cannot connect to database:**
```bash
# Verify volume mount
docker compose exec backend ls -la /app/data/
# Check permissions
docker compose exec backend stat /app/data/salarium.db
# Recreate with correct permissions
docker compose down
rm -rf ./data/sqlite
docker compose up -d
```

**Frontend shows 502 Bad Gateway:**
- Backend not ready (check health)
- Network issue (check `docker network ls`)
- nginx misconfiguration (check logs)

```bash
docker compose logs nginx
docker compose ps  # Check health status
docker network inspect salarium_salarium-network
```

## Best Practices

1. **Always use .env file** - Never hardcode secrets
2. **Regular backups** - Automate SQLite backup
3. **Monitor logs** - Set up log aggregation
4. **Health checks** - Ensure services are actually ready
5. **Resource limits** - Prevent resource exhaustion
6. **Security updates** - Regularly update base images
7. **Test locally first** - Validate changes before production
8. **Document changes** - Update this file with modifications

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vue Production Deployment](https://vuejs.org/guide/best-practices/production-deployment.html)
