# Djangalytics - Event Analytics Dashboard

A full-stack Django and React application that mimics the core functionality of PostHog's analytics product. This project demonstrates event ingestion, storage, and visualization in a real-time dashboard.

## Features

- **Event Capture**: Capture custom events via REST API
- **Real-time Dashboard**: View analytics with interactive charts
- **Event Visualization**: Bar charts, line charts, and pie charts
- **Live Feed**: Real-time stream of incoming events
- **Event Statistics**: Aggregated data by date and event type

## Tech Stack

### Backend
- **Django 5.2** - Web framework
- **Django REST Framework** - API development
- **SQLite** - Database (for development)
- **django-cors-headers** - CORS handling

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
make start         # Start both backend and frontend servers
```

That's it! The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

### Using Makefile Commands

```bash
# Development
make start         # Start both servers
make stop          # Stop all servers
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
- Python 3.8+
- Node.js 16+
- npm or yarn
- Make (optional, for using Makefile commands)

### Backend Setup

1. **Clone the repository** (if not already done)
2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install django djangorestframework django-cors-headers
   ```

4. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start Django development server**:
   ```bash
   python manage.py runserver
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

## Extending the Project

Consider adding:
- User authentication
- Event filtering and search
- Custom date ranges
- Export functionality
- Real-time WebSocket updates
- Database optimization for larger datasets
- Custom event properties visualization

## Learning Objectives

This project demonstrates:
- Django REST API development
- React component architecture
- Data visualization with charts
- API integration and error handling
- Real-time dashboard updates
- Full-stack application architecture