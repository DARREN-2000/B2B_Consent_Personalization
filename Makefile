.PHONY: help up down dev test build clean logs shell

# Default target
help:
	@echo ""
	@echo "ConsentHub Makefile targets:"
	@echo "  make up         - Start the full production stack (Docker Compose)"
	@echo "  make dev        - Start with hot-reload (development overrides)"
	@echo "  make down       - Stop and remove containers"
	@echo "  make test       - Run backend pytest suite"
	@echo "  make test-cov   - Run tests with coverage report"
	@echo "  make build      - Build Docker images"
	@echo "  make logs       - Tail logs for backend"
	@echo "  make shell      - Open a shell in the backend container"
	@echo "  make clean      - Remove volumes and images"
	@echo "  make helm-lint  - Lint the Helm chart"
	@echo ""

up:
	docker-compose up --build -d

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

down:
	docker-compose down

build:
	docker build -t consenthub/backend:latest ./backend
	docker build -t consenthub/frontend:latest ./frontend

test:
	cd backend && python -m pytest -v

test-cov:
	cd backend && python -m pytest --cov=app --cov-report=term-missing --cov-report=html

logs:
	docker-compose logs -f backend

shell:
	docker-compose exec backend /bin/sh

clean:
	docker-compose down -v --rmi local

helm-lint:
	helm lint helm/consenthub

helm-template:
	helm template consenthub helm/consenthub --debug
