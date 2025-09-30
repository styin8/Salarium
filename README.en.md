# Salarium — Simple Home Payroll

![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue?logo=githubactions) ![License](https://img.shields.io/badge/License-Private-lightgrey) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi) ![Vue 3](https://img.shields.io/badge/Vue_3-4FC08D?logo=vuedotjs) ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite) ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite)

Salarium is a lightweight demo app that brings together a FastAPI backend and a Vue 3 + Vite frontend to manage family or private payroll with a friendly developer experience.

## ✨ Highlights
- 🏠 Home/private payroll: designed for families or small, self-hosted use.
- 🔐 Auth-friendly: register/login flows optimized for local environments.
- 💸 Salary tracking: add, edit, and organize compensation data with ease.
- 📊 Quick insights: simple summaries to understand monthly totals.
- 🧱 SQLite first: portable, zero-setup local database.

## 🧩 Tech Stack
- FastAPI + Uvicorn for fast, type-safe APIs
- Tortoise ORM + SQLite for straightforward persistence
- Vue 3 + Vite for rapid frontend iteration and HMR
- Modular backend routes for clarity and easy maintenance

## 📁 Project Structure
```
backend/          # FastAPI app (routes, models, schemas, services, utils)
frontend/         # Vue 3 + Vite scaffold
README.en.md      # English documentation
README.zh.md      # Chinese documentation
```

## 🚀 Getting Started

### Prerequisites
- Python 3.12 (recommended)
- Node.js >= 18

### Backend Setup
Recommended (uv):
```
cd backend
uv sync
uv run uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Alternative (virtualenv):
```
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

On first run, the app initializes Tortoise ORM and creates `backend/salary.db`.

### Frontend Setup
```
cd frontend
npm install
npm run dev
```

Open the dev server URL (typically `http://localhost:5173`) and point your API calls to `http://127.0.0.1:8000`.

## 🖼 Screenshots
- Dashboard (placeholder): `docs/images/dashboard.png`
- Salaries (placeholder): `docs/images/salaries.png`

## 🏗 Architecture
```
[Vue 3 + Vite] → Axios → [FastAPI] → Tortoise ORM → [SQLite]
```

## 🛠 Development Notes
- 🧹 `.gitignore` excludes SQLite artifacts (`*.db`, `*.db-wal`, `*.db-shm`).
- 🔐 Prefer environment variables for secrets; avoid committing credentials.
- 🔄 Keep the backend on `127.0.0.1:8000` for smooth local integration.