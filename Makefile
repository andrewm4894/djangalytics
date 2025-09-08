# Djangalytics Makefile
# Common commands for development and testing

.PHONY: help setup install install-dev start stop test test-backend test-frontend clean lint lint-fix format format-check docker

# Default target
help:
	@echo "Djangalytics - Event Analytics Dashboard"
	@echo ""
	@echo "Available commands:"
	@echo "  setup          - Initial project setup (install dependencies)"
	@echo "  install        - Install all dependencies"
	@echo "  install-dev    - Install development dependencies (linters, formatters)"
	@echo "  start          - Start both backend and frontend servers"
	@echo "  start-backend  - Start Django development server"
	@echo "  start-frontend - Start React development server"
	@echo "  stop           - Stop all running servers"
	@echo "  stop-games     - Stop game servers only"
	@echo "  stop-all       - Stop all services (backend + frontend + games)"
	@echo "  test           - Run all tests (backend + frontend)"
	@echo "  test-backend   - Run Django tests only"
	@echo "  test-frontend  - Run React tests only"
	@echo "  lint           - Run linting on all code (flake8 + eslint)"
	@echo "  lint-fix       - Run linters with auto-fix where possible"
	@echo "  format         - Format code with black + prettier"
	@echo "  format-check   - Check code formatting without making changes"
	@echo "  pre-commit     - Install and setup pre-commit hooks"
	@echo "  clean          - Clean up generated files"
	@echo "  migrate        - Run Django database migrations"
	@echo "  seed-data      - Generate sample event data"
	@echo "  snake-test     - Test Snake game analytics integration"
	@echo "  start-snake    - Start Snake game demo app"
	@echo "  start-hedgehog - Start Flappy Hedgehog game demo app"
	@echo "  start-games    - Start both games on separate ports"
	@echo "  start-all      - Start analytics + frontend + both games"
	@echo "  lock           - Update uv.lock file"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-up      - Start with Docker Compose"

# Setup and Installation
setup: install migrate
	@echo "✅ Project setup complete!"
	@echo "Run 'make start' to launch the application"

install: install-backend install-frontend

install-dev: install-backend install-frontend
	@echo "🛠️  Installing development dependencies with uv..."
	uv sync --dev
	cd frontend && npm install --save-dev prettier

install-backend:
	@echo "📦 Installing Python dependencies with uv..."
	uv sync

install-frontend:
	@echo "📦 Installing Node.js dependencies..."
	cd frontend && npm install

# Development Servers
start:
	@echo "🚀 Starting Djangalytics..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:3000"
	@$(MAKE) start-backend &
	@sleep 3
	@$(MAKE) start-frontend

start-backend:
	@echo "🐍 Starting Django backend with uv..."
	uv run python manage.py runserver

start-frontend:
	@echo "⚛️  Starting React frontend..."
	cd frontend && npm start

stop:
	@echo "🛑 Stopping all servers..."
	@pkill -f "python.*runserver" || true
	@pkill -f "node.*react-scripts" || true
	@echo "✅ All servers stopped"

# Testing
test: test-backend test-frontend
	@echo "✅ All tests completed!"

test-backend:
	@echo "🧪 Running Django tests with uv..."
	uv run python manage.py test analytics

test-frontend:
	@echo "🧪 Running React tests..."
	cd frontend && npm test -- --watchAll=false --coverage --testTimeout=10000

# Database Operations
migrate:
	@echo "🗄️  Running database migrations with uv..."
	uv run python manage.py makemigrations
	uv run python manage.py migrate

seed-data:
	@echo "🌱 Setting up demo projects..."
	uv run python manage.py setup_projects
	@echo "🌱 Generating sample event data..."
	uv run python manage.py seed_events

# Code Quality & Linting
lint: lint-backend lint-frontend
	@echo "✅ All linting completed!"

lint-fix: lint-backend-fix lint-frontend-fix
	@echo "✅ All linting with fixes completed!"

lint-backend:
	@echo "🔍 Linting Python code with uv..."
	uv run flake8 .

lint-backend-fix:
	@echo "🔧 Linting and fixing Python code with uv..."
	uv run black .
	uv run isort .

lint-frontend:
	@echo "🔍 Linting React code..."
	cd frontend && npm run lint

lint-frontend-fix:
	@echo "🔧 Linting and fixing React code..."
	cd frontend && npm run lint:fix

format: format-backend format-frontend
	@echo "✅ All code formatted!"

format-check: format-check-backend format-check-frontend
	@echo "✅ Format check completed!"

format-backend:
	@echo "✨ Formatting Python code with uv..."
	uv run black .
	uv run isort .

format-check-backend:
	@echo "🔍 Checking Python code format with uv..."
	uv run black . --check
	uv run isort . --check-only

format-frontend:
	@echo "✨ Formatting React code..."
	cd frontend && npm run format

format-check-frontend:
	@echo "🔍 Checking React code format..."
	cd frontend && npm run format:check

# Pre-commit hooks
pre-commit: install-dev
	@echo "🪝 Installing pre-commit hooks with uv..."
	uv run pre-commit install
	@echo "✅ Pre-commit hooks installed! They will run automatically on git commit."

pre-commit-run:
	@echo "🪝 Running pre-commit on all files with uv..."
	uv run pre-commit run --all-files

# Maintenance
clean:
	@echo "🧹 Cleaning up generated files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf frontend/build
	rm -rf frontend/node_modules/.cache
	@echo "✅ Cleanup complete"

clean-deep: clean
	@echo "🧹 Deep cleaning (removes node_modules and venv)..."
	rm -rf frontend/node_modules
	rm -rf venv
	rm -f db.sqlite3
	@echo "✅ Deep cleanup complete"

lock:
	@echo "🔒 Updating uv.lock file..."
	uv lock
	@echo "✅ Dependencies locked"

# Docker Operations
docker-build:
	@echo "🐳 Building Docker images..."
	docker build -t djangalytics-backend .
	cd frontend && docker build -t djangalytics-frontend .

docker-up:
	@echo "🐳 Starting with Docker Compose..."
	docker-compose up -d

docker-down:
	@echo "🐳 Stopping Docker containers..."
	docker-compose down

# Development Utilities
shell:
	@echo "🐍 Opening Django shell with uv..."
	uv run python manage.py shell

logs:
	@echo "📋 Showing recent logs..."
	tail -f /tmp/djangalytics.log || echo "No log file found"

status:
	@echo "📊 System Status"
	@echo "=================="
	@echo "Backend Status:"
	@curl -s http://localhost:8000/api/stats/ > /dev/null && echo "✅ Backend running" || echo "❌ Backend not running"
	@echo "Frontend Status:"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend running" || echo "❌ Frontend not running"
	@echo ""
	@echo "Database:"
	@[ -f db.sqlite3 ] && echo "✅ Database exists ($(shell du -h db.sqlite3 | cut -f1))" || echo "❌ Database not found"
	@echo ""
	@echo "Dependencies:"
	@[ -f uv.lock ] && echo "✅ Python dependencies (uv.lock found)" || echo "❌ Python dependencies not installed (run: make install)"
	@[ -d frontend/node_modules ] && echo "✅ Node modules installed" || echo "❌ Node modules not found"

# Quick Development Commands
dev: setup start
	@echo "🎉 Development environment is ready!"

quick-test:
	@echo "⚡ Running quick tests with uv..."
	uv run python manage.py test analytics.test_models --verbosity=1

api-test:
	@echo "🔌 Testing API endpoints with uv..."
	uv run python test_api.py

snake-test:
	@echo "🐍 Testing Snake game analytics with uv..."
	uv run python test_snake_analytics.py

start-snake:
	@echo "🐍 Starting Snake game server..."
	@echo "Snake game will be available at http://localhost:8081"
	cd example-apps/snake-game && python -m http.server 8081

start-hedgehog:
	@echo "🦔 Starting Flappy Hedgehog game server..."
	@echo "Flappy Hedgehog game will be available at http://localhost:8082"
	cd example-apps/flappy-hedgehog && python -m http.server 8082

start-games:
	@echo "🎮 Starting both games on separate ports..."
	@echo "Snake game: http://localhost:8081"
	@echo "Flappy Hedgehog: http://localhost:8082"
	@echo "Press Ctrl+C to stop all games"
	@$(MAKE) start-snake &
	@sleep 2
	@$(MAKE) start-hedgehog

start-all:
	@echo "🚀 Starting complete Djangalytics demo environment..."
	@echo ""
	@echo "Services will be available at:"
	@echo "  📊 Analytics Backend:  http://localhost:8000"
	@echo "  🖥️  Analytics Frontend: http://localhost:3000"
	@echo "  🐍 Snake Game:         http://localhost:8081"
	@echo "  🦔 Flappy Hedgehog:    http://localhost:8082"
	@echo ""
	@echo "Starting services..."
	@$(MAKE) start-backend &
	@sleep 3
	@$(MAKE) start-frontend &
	@sleep 3
	@$(MAKE) start-games

stop-games:
	@echo "🛑 Stopping game servers..."
	@pkill -f "python.*http.server.*808[12]" || true
	@echo "✅ Game servers stopped"

stop-all: stop stop-games
	@echo "🛑 All services stopped"

reset-db:
	@echo "🔄 Resetting database..."
	rm -f db.sqlite3
	@$(MAKE) migrate
	@$(MAKE) seed-data
	@echo "✅ Database reset complete"

# Production-like testing
build-frontend:
	@echo "🏗️  Building frontend for production..."
	cd frontend && npm run build

serve-production:
	@echo "🚀 Serving production build..."
	cd frontend && npx serve -s build -l 3000

# Environment info
info:
	@echo "🔍 Environment Information"
	@echo "=========================="
	@echo "Python: $$(python3 --version 2>/dev/null || python --version 2>/dev/null || echo 'Not found')"
	@echo "Node.js: $$(node --version 2>/dev/null || echo 'Not found')"
	@echo "npm: $$(npm --version 2>/dev/null || echo 'Not found')"
	@echo "Django: $$(./venv/bin/python -c 'import django; print(django.get_version())' 2>/dev/null || echo 'Not installed')"
	@echo "React: $$(cd frontend && npm list react --depth=0 2>/dev/null | grep react@ | cut -d@ -f2 || echo 'Not installed')"
	@echo ""
	@echo "Project Structure:"
	@echo "- Backend: Django $(shell ./venv/bin/python -c 'import django; print(django.get_version())' 2>/dev/null || echo 'N/A')"
	@echo "- Frontend: React $(cd frontend && npm list react --depth=0 2>/dev/null | grep react@ | cut -d@ -f2 || echo 'N/A')"
	@echo "- Database: SQLite"
	@echo "- Charts: Recharts"