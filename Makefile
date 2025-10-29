.PHONY: help build up down logs clean restart status

help: ## Show this help message
	@echo "Salarium Docker Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker images
	docker compose build

up: ## Start services
	docker compose up -d
	@echo "Frontend: http://localhost:8080"
	@echo "Backend API: http://localhost:8080/api/docs"

down: ## Stop services
	docker compose down

logs: ## Show logs (use CTRL+C to exit)
	docker compose logs -f

clean: ## Remove containers, volumes, and data
	docker compose down -v
	rm -rf ./data/sqlite

restart: down up ## Restart services

status: ## Show service status
	docker compose ps

dev-backend: ## Run backend in development mode
	cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev
