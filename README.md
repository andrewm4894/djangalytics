# Djangalytics - Event Analytics Dashboard

A full-stack Django and React application that mimics the core functionality of PostHog's analytics product. This project demonstrates event ingestion, storage, and visualization in a real-time dashboard with live demo games.

## Features

### 📊 Core Analytics
- **Event Capture**: Capture custom events via REST API
- **Real-time Dashboard**: View analytics with interactive charts and modern UI
- **Event Visualization**: Bar charts, line charts, and pie charts
- **Live Events Feed**: Beautiful real-time stream with icons, badges, and animations
- **Event Statistics**: Aggregated data by date and event type
- **Project-based Analytics**: Multi-project support with API key authentication

### 🎮 Demo Applications
- **Snake Game**: Classic snake game with comprehensive analytics integration
- **Flappy Hedgehog**: Flappy Bird-style game with hedgehog character
- **Clean Game UI**: Modern side-panel layouts with responsive design
- **Real-time Event Tracking**: Every game action generates analytics events

## Tech Stack

### Backend
- **Django 5.2** - Web framework
- **Django REST Framework** - API development
- **SQLite** - Database (for development)
- **django-cors-headers** - CORS handling
- **uv** - Fast Python package management

### Frontend
- **React 18** - Frontend framework
- **Recharts** - Chart visualization library
- **Axios** - HTTP client

## Project Structure

```
djangalytics/
├── djangalytics/          # Django project settings
├── analytics/             # Django app for analytics
├── frontend/              # React application
├── venv/                  # Python virtual environment
├── manage.py              # Django management script
├── test_api.py           # API testing script
└── README.md             # This file
```

## Quick Start

The fastest way to get started is using our Makefile:

```bash
make help          # See all available commands
make setup         # Install dependencies and set up the project
make start-all     # Start complete demo environment
```

That's it! The complete demo will be available at:
- **📊 Analytics Dashboard**: http://localhost:3000
- **🔧 Analytics Backend**: http://localhost:8000
- **🐍 Snake Game**: http://localhost:8081
- **🦔 Flappy Hedgehog**: http://localhost:8082

### Using Makefile Commands

```bash
# Development
make start         # Start backend and frontend only
make start-all     # Start complete demo (analytics + games)
make start-games   # Start just the demo games
make stop-all      # Stop all services
make status        # Check system status

# Testing
make test          # Run all tests
make test-backend  # Run Django tests only
make test-frontend # Run React tests only
make api-test      # Test API endpoints

# Database
make migrate       # Run database migrations
make seed-data     # Generate sample event data
make reset-db      # Reset database with fresh data

# Maintenance
make clean         # Clean up generated files
make info          # Show environment information
```

## Manual Installation & Setup

### Prerequisites
- Python 3.10+
- **uv** (recommended) or pip for Python package management
- Node.js 16+
- npm or yarn
- Make (optional, for using Makefile commands)

### Backend Setup

1. **Clone the repository** (if not already done)
2. **Install Python dependencies with uv (recommended)**:
   ```bash
   uv sync
   ```
   
   Or with pip:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install django djangorestframework django-cors-headers
   ```

3. **Run database migrations**:
   ```bash
   uv run python manage.py migrate
   ```

4. **Start Django development server**:
   ```bash
   uv run python manage.py runserver
   ```
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Start React development server**:
   ```bash
   npm start
   ```
   The frontend will be available at `http://localhost:3000`

## API Endpoints

### POST /api/capture_event/
Capture a new event.

**Request Body**:
```json
{
  "event_name": "user_signup",
  "timestamp": "2024-01-01T12:00:00Z",  // Optional
  "properties": {                       // Optional
    "user_id": 123,
    "source": "web"
  }
}
```

**Response**:
```json
{
  "id": 1,
  "event_name": "user_signup",
  "timestamp": "2024-01-01T12:00:00Z",
  "message": "Event captured successfully"
}
```

### GET /api/stats/
Get aggregated analytics data.

**Response**:
```json
{
  "daily_stats": [...],      // Events grouped by date and type
  "event_counts": [...],     // Total counts by event type
  "recent_events": [...],    // Last 20 events
  "total_events": 150        // Total event count
}
```

### GET /api/events/
Get recent events (last 50).

## Usage

1. **Start both servers** (Django on :8000 and React on :3000)
2. **Open the dashboard** at `http://localhost:3000`
3. **Capture events** using:
   - The web interface (manual entry or quick buttons)
   - Direct API calls
   - The test script: `python test_api.py`

## Testing

### Comprehensive Test Suite

The project includes extensive tests for both backend and frontend:

```bash
# Run all tests
make test

# Run individual test suites
make test-backend   # Django model, view, and serializer tests
make test-frontend  # React component tests with mocking
make api-test       # Live API endpoint testing
```

### Backend Tests (Django)
- **Model Tests**: Event creation, validation, ordering
- **View Tests**: API endpoint functionality, error handling  
- **Serializer Tests**: Data validation and serialization
- **15 total test cases** covering all core functionality

### Frontend Tests (React)
- **Component Tests**: Rendering, user interactions
- **API Integration Tests**: Mocked axios calls
- **Error Handling Tests**: Network failures, API errors
- **State Management Tests**: Loading states, form validation

### Sample Data Generation

Generate sample data for testing:

```bash
make seed-data     # Using Makefile
# OR
python test_api.py # Direct script execution
```

This creates 20 sample events with random types and timestamps over the last 7 days.

## Dashboard Features

- **Event Capture Form**: Manual event entry
- **Quick Event Buttons**: One-click common events
- **Event Distribution Chart**: Bar chart of event types
- **Daily Trends Chart**: Line chart of events over time
- **Event Breakdown**: Pie chart showing proportions
- **Live Feed**: Real-time list of recent events
- **Auto-refresh**: Dashboard updates every 5 seconds

## Docker Support

Run the entire application with Docker:

```bash
# Build and start with Docker Compose
make docker-up

# Or manually
docker-compose up --build
```

The Docker setup includes:
- **Backend**: Django app with PostgreSQL
- **Frontend**: React development server  
- **Database**: PostgreSQL container
- **Hot Reload**: Code changes reflect immediately

## Development Notes

- CORS is configured to allow requests from `http://localhost:3000`
- The SQLite database file (`db.sqlite3`) is created automatically
- Events are stored with timestamps, names, and optional JSON properties
- The frontend polls the backend every 5 seconds for live updates
- Comprehensive test coverage for both backend and frontend
- Makefile provides convenient development commands

## 🚀 Demo Experience

### Quick Demo Walkthrough:
1. **Start everything**: `make start-all`
2. **Open analytics dashboard**: http://localhost:3000
3. **Play Snake game**: http://localhost:8081 - See events flow in real-time!
4. **Play Flappy Hedgehog**: http://localhost:8082 - Watch your analytics grow!
5. **Observe the dashboard**: Beautiful event feed with icons, colors, and animations

### What You'll See:
- 🚀 App opened events when games load
- 🎮 Game started events with session data
- 🍎 Food eaten events (Snake) with scores
- 🪶 Flap events (Hedgehog) with positions
- 🏆 High score achievements with celebration data
- 💀 Game over events with detailed performance metrics

## Extending the Project

Consider adding:
- Multi-tenant dashboard with project switching
- Advanced event filtering and search
- Custom date ranges and time periods
- Event funnel analysis
- Real-time WebSocket updates
- Event schema validation
- A/B testing framework integration
- Custom dashboard creation

## Learning Objectives

This project demonstrates:
- Django REST API development
- React component architecture
- Data visualization with charts
- API integration and error handling
- Real-time dashboard updates
- Full-stack application architecture