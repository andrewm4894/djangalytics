# Djangalytics Architecture

This document outlines the architecture, data flow, and technical design decisions for the Djangalytics event analytics platform.

## System Overview

Djangalytics is a full-stack web application that captures, stores, and visualizes event data in real-time. It follows a modern web architecture with a REST API backend and a reactive frontend.

```mermaid
graph TB
    subgraph "Frontend (React)"
        A[Dashboard Component]
        B[EventCapture Component]
        C[Chart Components]
        D[Live Feed]
    end
    
    subgraph "Backend (Django)"
        E[REST API Endpoints]
        F[Event Models]
        G[Analytics Views]
        H[Database Layer]
    end
    
    subgraph "Database"
        I[(SQLite)]
    end
    
    B -->|POST /api/capture_event/| E
    A -->|GET /api/stats/| E
    D -->|GET /api/events/| E
    E --> F
    F --> H
    H --> I
    G --> F
    E --> G
```

## Component Architecture

### Backend Architecture (Django)

```mermaid
graph TD
    subgraph "Django Application"
        subgraph "djangalytics (Project)"
            A[settings.py]
            B[urls.py]
            C[wsgi.py/asgi.py]
        end
        
        subgraph "analytics (App)"
            D[models.py]
            E[views.py]
            F[serializers.py]
            G[urls.py]
        end
        
        subgraph "Database"
            H[Event Model]
            I[(SQLite)]
        end
        
        subgraph "Middleware"
            J[CORS Middleware]
            K[Django REST Framework]
        end
    end
    
    A --> J
    B --> G
    G --> E
    E --> F
    F --> D
    D --> H
    H --> I
    J --> K
    K --> E
```

### Frontend Architecture (React)

```mermaid
graph TD
    subgraph "React Application"
        A[App.js]
        
        subgraph "Components"
            B[Dashboard.js]
            C[EventCapture.js]
        end
        
        subgraph "Chart Library"
            D[Recharts]
            E[BarChart]
            F[LineChart]
            G[PieChart]
        end
        
        subgraph "HTTP Client"
            H[Axios]
        end
        
        subgraph "Styling"
            I[App.css]
        end
    end
    
    A --> B
    A --> C
    B --> D
    D --> E
    D --> F
    D --> G
    B --> H
    C --> H
    A --> I
```

## Data Flow

### Event Capture Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FC as EventCapture Component
    participant API as Django REST API
    participant DB as SQLite Database
    participant D as Dashboard
    
    U->>FC: Enter event name
    U->>FC: Click "Capture Event"
    FC->>API: POST /api/capture_event/
    Note over FC,API: {event_name, timestamp, properties}
    API->>DB: Store event record
    DB-->>API: Confirm storage
    API-->>FC: 201 Created response
    FC->>FC: Show success message
    FC->>FC: Clear form
    
    Note over D: Auto-refresh every 5s
    D->>API: GET /api/stats/
    API->>DB: Query aggregated data
    DB-->>API: Return statistics
    API-->>D: Statistics JSON
    D->>D: Update charts and live feed
```

### Dashboard Data Flow

```mermaid
flowchart TD
    A[Dashboard Component Loads] --> B[Initial API Call]
    B --> C[GET /api/stats/]
    C --> D[Process Response Data]
    
    D --> E[Update Event Counts]
    D --> F[Update Daily Trends]
    D --> G[Update Recent Events]
    
    E --> H[Render Bar Chart]
    F --> I[Render Line Chart]
    F --> J[Render Pie Chart]
    G --> K[Render Live Feed]
    
    L[5 Second Timer] --> M[Auto-refresh]
    M --> C
    
    N[Manual Refresh Button] --> C
    
    O[Error Handling] --> P[Display Error Message]
    C --> O
```

## Database Schema

### Event Model

```mermaid
erDiagram
    Event {
        int id PK
        varchar event_name
        datetime timestamp
        json properties
    }
    
    Event ||--|| EventStats : aggregates_to
    
    EventStats {
        varchar event_name
        date date
        int count
    }
```

**Event Table Structure:**
- `id`: Primary key (auto-increment)
- `event_name`: String field (max 100 chars) - the type of event
- `timestamp`: DateTime field with auto-generated timestamp
- `properties`: JSON field for additional event metadata (optional)

## API Design

### REST Endpoints

```mermaid
graph LR
    subgraph "API Endpoints"
        A[POST /api/capture_event/]
        B[GET /api/stats/]
        C[GET /api/events/]
    end
    
    subgraph "Request/Response"
        D[Event Creation Request]
        E[Statistics Response]
        F[Recent Events Response]
    end
    
    A --> D
    B --> E
    C --> F
```

#### POST /api/capture_event/
**Purpose**: Create new event records
**Authentication**: None (open endpoint)
**Rate Limiting**: None (development)

**Request Schema**:
```json
{
  "event_name": "string (required)",
  "timestamp": "ISO datetime (optional)",
  "properties": "object (optional)"
}
```

#### GET /api/stats/
**Purpose**: Retrieve aggregated analytics data
**Caching**: None (real-time data)

**Response Schema**:
```json
{
  "daily_stats": [{"date": "date", "event_name": "string", "count": "int"}],
  "event_counts": [{"event_name": "string", "count": "int"}],
  "recent_events": [{"id": "int", "event_name": "string", "timestamp": "datetime"}],
  "total_events": "int"
}
```

## Technology Stack

### Backend Dependencies

```mermaid
graph TD
    A[Django 5.2] --> B[Core Framework]
    C[Django REST Framework] --> D[API Development]
    E[django-cors-headers] --> F[CORS Handling]
    G[SQLite] --> H[Database]
    
    I[Python 3.8+] --> A
    I --> C
    I --> E
```

### Frontend Dependencies

```mermaid
graph TD
    A[React 18] --> B[UI Framework]
    C[Recharts] --> D[Data Visualization]
    E[Axios] --> F[HTTP Client]
    G[Create React App] --> H[Build Tooling]
    
    I[Node.js 16+] --> A
    I --> C
    I --> E
    I --> G
```

## Deployment Architecture

### Development Environment

```mermaid
graph TB
    subgraph "Developer Machine"
        subgraph "Backend"
            A[Django Dev Server]
            B[Port 8000]
        end
        
        subgraph "Frontend"
            C[React Dev Server]
            D[Port 3000]
        end
        
        subgraph "Database"
            E[SQLite File]
        end
    end
    
    C -->|API Calls| A
    A --> E
```

### Production Considerations

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Web Server"
            A[Nginx/Apache]
        end
        
        subgraph "Application Server"
            B[Gunicorn/uWSGI]
            C[Django Application]
        end
        
        subgraph "Database"
            D[PostgreSQL/MySQL]
        end
        
        subgraph "Static Files"
            E[CDN/Static Server]
        end
        
        subgraph "Client"
            F[React Build]
        end
    end
    
    A --> B
    A --> E
    A --> F
    B --> C
    C --> D
```

## Security Considerations

### CORS Configuration
- Configured to allow `localhost:3000` in development
- Should be restricted to specific domains in production

### API Security
- Currently uses `AllowAny` permissions (development)
- Production should implement authentication/authorization
- Consider rate limiting for event capture endpoint

### Data Validation
- Django REST Framework serializers handle input validation
- Client-side validation provides immediate feedback
- Server-side validation ensures data integrity

## Performance Considerations

### Database Optimization
```mermaid
graph TD
    A[Event Model] --> B[Index on timestamp]
    A --> C[Index on event_name]
    D[Query Optimization] --> E[Limit recent events to 50]
    D --> F[Aggregate queries for stats]
    D --> G[Date-based filtering for trends]
```

### Frontend Optimization
- Auto-refresh interval: 5 seconds (configurable)
- Chart re-rendering optimized by React
- Error boundary handling for API failures
- Loading states for better UX

### Scalability Considerations
- SQLite suitable for development/small scale
- Consider PostgreSQL for production
- Event table will grow quickly - implement archiving
- Add caching layer (Redis) for frequently accessed stats
- Consider event streaming for high-volume scenarios

## Development Workflow

```mermaid
graph TD
    A[Start Development] --> B[Activate Virtual Environment]
    B --> C[Start Django Server]
    C --> D[Start React Dev Server]
    D --> E[Both Servers Running]
    
    F[Code Changes] --> G[Hot Reload]
    G --> H[Test Changes]
    H --> I{Changes Good?}
    I -->|Yes| J[Continue Development]
    I -->|No| F
    J --> F
    
    K[API Testing] --> L[Run test_api.py]
    L --> M[Generate Sample Data]
    M --> N[Verify Dashboard Updates]
```

## Future Enhancements

### Phase 1: Core Improvements
- User authentication and authorization
- Event filtering and search functionality
- Custom date range selection
- Export functionality (CSV, JSON)

### Phase 2: Advanced Features
- Real-time updates via WebSockets
- Custom dashboard creation
- Event schema validation
- A/B testing framework integration

### Phase 3: Scale & Performance
- Microservices architecture
- Event streaming pipeline
- Advanced analytics and ML insights
- Multi-tenant support

This architecture provides a solid foundation for an analytics platform while maintaining simplicity and clarity for learning purposes.