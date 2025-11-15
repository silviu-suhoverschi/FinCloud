.PHONY: help dev up down logs clean test lint build deploy migrate-budget migrate-portfolio migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start development environment
	docker-compose up -d

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs
	docker-compose logs -f

clean: ## Clean up containers and volumes
	docker-compose down -v
	rm -rf postgres_data redis_data minio_data

test: ## Run tests
	cd services/budget-service && pytest
	cd services/portfolio-service && pytest

lint: ## Run linters
	cd services/budget-service && ruff check . && black --check .
	cd services/portfolio-service && ruff check . && black --check .
	cd frontend && npm run lint

build: ## Build all Docker images
	docker-compose build

deploy-k8s: ## Deploy to Kubernetes
	helm upgrade --install fincloud infrastructure/helm/fincloud \
		--namespace fincloud \
		--create-namespace

setup: ## Initial setup
	cp .env.example .env
	@echo "Please edit .env with your configuration"
	@echo "Then run: make dev"

frontend-install: ## Install frontend dependencies
	cd frontend && npm install

services-install: ## Install Python dependencies for services
	cd services/budget-service && pip install -r requirements.txt
	cd services/portfolio-service && pip install -r requirements.txt

migrate-budget: ## Run budget service database migrations
	docker-compose exec budget-service alembic upgrade head

migrate-portfolio: ## Run portfolio service database migrations
	docker-compose exec portfolio-service alembic upgrade head

migrate: ## Run all database migrations
	docker-compose exec budget-service alembic upgrade head
	docker-compose exec portfolio-service alembic upgrade head
