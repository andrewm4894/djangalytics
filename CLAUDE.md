# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Djangalytics is a full-stack event analytics platform built with Django REST API backend and React frontend, similar to PostHog. It uses modern Python tooling with **uv** for fast dependency management, includes comprehensive project-based authentication, rate limiting, multi-source analytics, and demo games that showcase real-world analytics integration.

## Architecture

### Backend (Django)
- **Django 5.2** REST API with SQLite database (dev) / PostgreSQL (prod)
- **Project-based authentication** using API keys (`pk_...` public, `sk_...` secret)
- **Multi-model architecture**: `Project`, `Event`, `ProjectRateLimit`, `IPRateLimit`
- **Rate limiting**: Both IP-based (100/min) and project-based (1000/min default)
- **Source validation**: Projects can restrict allowed event sources

### Frontend (React)
- **React 18** with Create React App, Recharts for visualization
- **Real-time dashboard** with 5-second auto-refresh
- **Chart components**: Bar charts (event counts), line charts (daily trends), pie charts (breakdowns)
- **Live event feed** with rich styling and animations

### Demo Games Integration
- **Snake Game** (port 8081) and **Flappy Hedgehog** (port 8082)
- Comprehensive analytics integration with events like `app_opened`, `game_started`, `food_eaten`, `game_over`
- Show real-world patterns for event tracking in gaming applications

## Development Commands

### Setup & Installation
```bash
make setup         # Full setup (dependencies + database)
make install       # Install dependencies with uv
make install-dev   # Install with development dependencies
uv sync            # Manual dependency installation
uv sync --dev      # Manual dev dependencies installation
cd frontend && npm install
```

### Running Services
```bash
make start-all     # Complete demo (backend + frontend + games)
make start         # Backend + frontend only
make start-backend # Django server (port 8000) with uv
make start-frontend # React dev server (port 3000)
make start-games   # Demo games (ports 8081, 8082)
```

### Database Operations
```bash
make migrate       # Run Django migrations with uv
make seed-data     # Generate sample events
make reset-db      # Fresh database with sample data
uv run python manage.py makemigrations analytics  # Create new migrations
```

### Testing
```bash
make test          # All tests (backend + frontend)
make test-backend  # Django model/view/serializer tests with uv
make test-frontend # React component tests with mocking
make api-test      # Live API endpoint testing with uv
uv run python manage.py test analytics  # Specific app tests
cd frontend && npm test  # React tests only
```

### Code Quality & Linting
```bash
make install-dev   # Install development dependencies (linters, formatters)
make lint          # Run all linters (flake8 + eslint)
make lint-fix      # Run linters with auto-fix where possible
make format        # Format all code (black + prettier)
make format-check  # Check code formatting without making changes
make pre-commit    # Install pre-commit hooks for automatic linting
make pre-commit-run # Run pre-commit on all files manually
```

### Utilities
```bash
make status        # Check all services status
make clean         # Clean generated files
make info          # Environment information
make lock          # Update uv.lock file
uv run python manage.py shell  # Django shell
```

## Key Files & Structure

### Backend Core
- `djangalytics/settings.py` - CORS enabled for all origins (analytics pattern)
- `analytics/models.py` - Project/Event models with comprehensive indexing
- `analytics/views.py` - API endpoints with rate limiting and authentication
- `analytics/serializers.py` - DRF serializers for validation
- `analytics/utils.py` - Rate limiting utilities
- `analytics/tests.py` - Comprehensive test coverage

### Frontend Core
- `frontend/src/components/Dashboard.js` - Main analytics dashboard
- `frontend/src/components/EventCapture.js` - Event creation interface
- `frontend/src/config.js` - API configuration

### Demo Applications
- `example-apps/snake-game/` - Snake game with analytics integration
- `example-apps/flappy-hedgehog/` - Flappy Bird clone with event tracking

## Database Schema

### Project Model
- Multi-tenant system with API key authentication
- Configurable rate limits and allowed sources
- Automatic key generation: `pk_*` (public) and `sk_*` (secret)

### Event Model
- Project-scoped events with source tracking
- Rich metadata: user_id, session_id, user_agent, ip_address
- JSON properties field for flexible event data
- Optimized indexes for common queries

### Rate Limiting Models
- IP-based and project-based rate limiting
- Minute-bucket tracking for precise limits

## API Patterns

### Authentication
- API key via `api_key` parameter in request body or query params
- Project-based scoping for all operations
- Rate limiting enforced at both IP and project levels

### Event Capture
```bash
POST /api/capture_event/
{
  "api_key": "pk_...",
  "event_name": "user_signup",
  "source": "web",
  "properties": {"user_id": 123}
}
```

### Analytics Data
```bash
GET /api/stats/?api_key=pk_...  # Project-scoped stats
GET /api/events/?api_key=pk_... # Recent events
```

## Code Quality & Linting

The project uses comprehensive linting and formatting tools:

### Python Tools
- **flake8**: Linting and style checking
- **black**: Code formatting (100 char line length)
- **isort**: Import sorting with Django-aware configuration
- **bandit**: Security vulnerability scanning

### JavaScript/React Tools
- **ESLint**: Linting with React-specific rules
- **Prettier**: Code formatting with consistent style

### Pre-commit Hooks
- Automatic code quality checks on every commit
- Runs formatters, linters, and security checks
- Install with `make pre-commit`

### Configuration Files
- `.flake8`: Python linting configuration
- `pyproject.toml`: Project metadata, dependencies, and tool configuration (uv, black, isort, coverage)
- `frontend/package.json`: ESLint and Prettier configuration
- `.pre-commit-config.yaml`: Pre-commit hooks setup
- `uv.lock`: Locked dependency versions (generated by uv)

## Development Patterns

### Adding New Event Types
1. No schema changes needed - events are flexible via JSON properties
2. Update demo games or frontend to send new event types
3. Consider analytics dashboard visualization needs

### Rate Limiting Changes
- Modify limits in `analytics/utils.py`
- Project limits configurable via Project model
- IP limits are system-wide (currently 100/minute)

### Frontend Components
- Follow existing patterns in Dashboard.js and EventCapture.js
- Use Recharts for any new visualizations
- Maintain 5-second refresh pattern for real-time feel

### Testing Patterns
- Model tests for data validation
- View tests for API endpoints with authentication
- Frontend tests with mocked axios calls
- Integration tests via `test_api.py`

## Security Considerations

- CORS allows all origins (industry standard for analytics platforms)
- Security via API key authentication, not origin restrictions
- Rate limiting prevents abuse
- Input validation via DRF serializers
- IP tracking for security analytics

## Performance Notes

- SQLite adequate for development, use PostgreSQL for production
- Event table grows quickly - implement archiving strategy for scale
- Consider Redis caching for frequently accessed stats
- Database indexes optimized for common query patterns

This project demonstrates real-world patterns for building analytics platforms with proper authentication, rate limiting, and multi-source event tracking.

**Requirements**: Python 3.10+ and uv for modern package management.