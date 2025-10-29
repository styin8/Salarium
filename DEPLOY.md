# Salarium Docker 部署指南 / Docker Deployment Guide

[English](#english) | [中文](#chinese)

<a name="english"></a>
## English

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd salarium
```

2. **Configure environment variables (optional)**
```bash
cp .env.example .env
# Edit .env to set your JWT_SECRET and other configurations
```

3. **Start the application**
```bash
docker compose up -d --build
```

4. **Access the application**
- Frontend: http://localhost:8080
- Backend API docs: http://localhost:8080/api/docs

5. **Stop the application**
```bash
docker compose down
```

### Architecture

The deployment consists of two services:

- **Backend**: FastAPI application running on Python 3.12-slim with Uvicorn (2 workers by default)
- **Frontend**: Vue 3 SPA served by Nginx with reverse proxy to backend at `/api`

### Data Persistence

SQLite database is persisted in `./data/sqlite` directory on the host machine. The database file will be created automatically on first run.

To backup your data:
```bash
cp -r ./data/sqlite ./backup-$(date +%Y%m%d)
```

### Environment Variables

All environment variables can be configured in `.env` file (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | `super-secret-change-me` | Secret key for JWT token signing ⚠️ Change in production! |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token expiration time (24 hours) |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |
| `UVICORN_WORKERS` | `2` | Number of Uvicorn worker processes |
| `FRONTEND_PORT` | `8080` | Host port for frontend access |

### Health Checks

The backend service includes a health check that polls `/docs` endpoint every 30 seconds. The frontend service will only start after the backend is healthy.

### Logs

View logs for all services:
```bash
docker compose logs -f
```

View logs for a specific service:
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### Development Tips

**Rebuild after code changes:**
```bash
docker compose up -d --build
```

**Access backend container shell:**
```bash
docker compose exec backend sh
```

**Access frontend container shell:**
```bash
docker compose exec frontend sh
```

### Upgrading to PostgreSQL/MySQL

To switch from SQLite to PostgreSQL or MySQL:

1. Add database service to `docker-compose.yml`:
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: salarium
      POSTGRES_USER: salarium
      POSTGRES_PASSWORD: your-password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - salarium-network

volumes:
  postgres-data:
```

2. Update backend dependencies in `requirements.txt`:
```
# For PostgreSQL
asyncpg

# For MySQL
aiomysql
```

3. Update `config.py` to use `DATABASE_URL` environment variable:
```python
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite://{DB_PATH}")
```

4. Update backend environment in `docker-compose.yml`:
```yaml
backend:
  environment:
    - DATABASE_URL=postgres://salarium:your-password@postgres:5432/salarium
  depends_on:
    postgres:
      condition: service_healthy
```

### Troubleshooting

**Port already in use:**
```bash
# Change frontend port in .env
FRONTEND_PORT=3000
```

**Database permissions:**
```bash
# Ensure data directory has correct permissions
mkdir -p ./data/sqlite
chmod 755 ./data/sqlite
```

**Backend not starting:**
```bash
# Check logs
docker compose logs backend

# Rebuild without cache
docker compose build --no-cache backend
docker compose up -d backend
```

---

<a name="chinese"></a>
## 中文

### 快速启动

1. **克隆仓库**
```bash
git clone <repository-url>
cd salarium
```

2. **配置环境变量（可选）**
```bash
cp .env.example .env
# 编辑 .env 设置您的 JWT_SECRET 和其他配置
```

3. **启动应用**
```bash
docker compose up -d --build
```

4. **访问应用**
- 前端界面：http://localhost:8080
- 后端 API 文档：http://localhost:8080/api/docs

5. **停止应用**
```bash
docker compose down
```

### 架构说明

部署包含两个服务：

- **Backend（后端）**：基于 Python 3.12-slim 运行的 FastAPI 应用，使用 Uvicorn（默认 2 个 worker）
- **Frontend（前端）**：由 Nginx 托管的 Vue 3 单页应用，并将 `/api` 反向代理到后端

### 数据持久化

SQLite 数据库持久化在宿主机的 `./data/sqlite` 目录。数据库文件会在首次运行时自动创建。

备份数据：
```bash
cp -r ./data/sqlite ./backup-$(date +%Y%m%d)
```

### 环境变量

所有环境变量可在 `.env` 文件中配置（参考 `.env.example`）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `JWT_SECRET` | `super-secret-change-me` | JWT 令牌签名密钥 ⚠️ 生产环境请修改！ |
| `JWT_ALGORITHM` | `HS256` | JWT 签名算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 令牌过期时间（24 小时） |
| `CORS_ORIGINS` | `*` | 允许的 CORS 源（逗号分隔） |
| `UVICORN_WORKERS` | `2` | Uvicorn 工作进程数 |
| `FRONTEND_PORT` | `8080` | 前端访问的宿主机端口 |

### 健康检查

后端服务包含健康检查，每 30 秒轮询 `/docs` 端点。前端服务仅在后端健康后才会启动。

### 日志查看

查看所有服务日志：
```bash
docker compose logs -f
```

查看特定服务日志：
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### 开发提示

**代码修改后重新构建：**
```bash
docker compose up -d --build
```

**进入后端容器 Shell：**
```bash
docker compose exec backend sh
```

**进入前端容器 Shell：**
```bash
docker compose exec frontend sh
```

### 升级到 PostgreSQL/MySQL

从 SQLite 切换到 PostgreSQL 或 MySQL：

1. 在 `docker-compose.yml` 中添加数据库服务：
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: salarium
      POSTGRES_USER: salarium
      POSTGRES_PASSWORD: your-password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - salarium-network

volumes:
  postgres-data:
```

2. 更新 `requirements.txt` 中的后端依赖：
```
# PostgreSQL
asyncpg

# MySQL
aiomysql
```

3. 更新 `config.py` 使用 `DATABASE_URL` 环境变量：
```python
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite://{DB_PATH}")
```

4. 更新 `docker-compose.yml` 中的后端环境变量：
```yaml
backend:
  environment:
    - DATABASE_URL=postgres://salarium:your-password@postgres:5432/salarium
  depends_on:
    postgres:
      condition: service_healthy
```

### 故障排除

**端口已被占用：**
```bash
# 在 .env 中修改前端端口
FRONTEND_PORT=3000
```

**数据库权限问题：**
```bash
# 确保数据目录有正确的权限
mkdir -p ./data/sqlite
chmod 755 ./data/sqlite
```

**后端无法启动：**
```bash
# 查看日志
docker compose logs backend

# 无缓存重新构建
docker compose build --no-cache backend
docker compose up -d backend
```
