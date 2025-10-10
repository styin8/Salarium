# Salarium — 薪资管理

![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue?logo=githubactions) ![License](https://img.shields.io/badge/License-Private-lightgrey) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi) ![Vue 3](https://img.shields.io/badge/Vue_3-4FC08D?logo=vuedotjs) ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite) ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite)

Salarium 是一个轻量的演示应用，结合 FastAPI 后端与 Vue 3 + Vite 前端，面向家庭或私有化的薪资管理场景，注重简单易用与良好的开发体验。

## ✨ 亮点
- 🏠 家庭/私有薪资：适用于家庭或小型自托管场景。
- 🔐 认证就绪：本地环境的注册/登录流程友好。
- 💸 薪资记录：轻松新增、编辑与整理薪酬数据。
- 📊 快速概览：简单汇总以了解月度总额等信息。
- 🧱 SQLite 优先：便携、零配置的本地数据库。

## 🧩 技术栈
- FastAPI + Uvicorn：高性能、类型安全的后端 API。
- Tortoise ORM + SQLite：简单直观的持久化方案。
- Vue 3 + Vite：前端开发高效，支持 HMR 热更新。
- 模块化后端路由：清晰的代码结构与易维护性。

## 📁 目录结构
```
backend/          # FastAPI 应用（routes、models、schemas、services、utils）
frontend/         # Vue 3 + Vite 前端项目
README.en.md      # 英文文档
README.zh.md      # 中文文档
```

## 🚀 快速开始

### 前置条件
- Python 3.12（推荐）
- Node.js >= 18

### 后端启动
推荐（uv）：
```
cd backend
uv sync
uv run uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

备选（virtualenv）：
```
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

首次运行会初始化 Tortoise ORM 并创建 `backend/salary.db`。

### 前端启动
```
cd frontend
npm install
npm run dev
```

打开开发服务器（通常为 `http://localhost:5173`），将 API 指向 `http://127.0.0.1:8000`。

## 🖼 截图
- 仪表盘（占位）：`docs/images/dashboard.png`
- 薪资页面（占位）：`docs/images/salaries.png`

## 🏗 架构
```
[Vue 3 + Vite] → Axios → [FastAPI] → Tortoise ORM → [SQLite]
```

## 🛠 开发说明
- 🧹 `.gitignore` 已忽略 SQLite 产物（`*.db`、`*.db-wal`、`*.db-shm`）。
- 🔐 机密信息请使用环境变量管理，避免提交凭据。
- 🔄 后端建议在 `127.0.0.1:8000` 运行，便于前端对接。