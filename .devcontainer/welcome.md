# 🎉 Welcome to Djangalytics Development Environment!

Your complete analytics platform is ready to explore in GitHub Codespaces! Everything has been automatically set up and is running.

## 🚀 What's Running

Your development environment includes:

- **🐍 Django Backend** (Port 8000) - REST API with authentication & rate limiting
- **⚛️ React Frontend** (Port 3000) - Real-time analytics dashboard  
- **🎮 Snake Game** (Port 8081) - Demo game with analytics integration
- **🦔 Flappy Hedgehog** (Port 8082) - Another demo game with event tracking

## 🎯 Quick Start

### 1. Open the Services
Click on the "Ports" tab in VS Code and open these services:

- **Analytics Dashboard**: Port 3000 - Main analytics interface
- **Django Admin**: Port 8000/admin - Backend administration
- **API Docs**: Port 8000/api - REST API endpoints

### 2. Play the Demo Games
Open the games and play them to generate analytics events:

- **Snake Game**: Port 8081 - Classic snake with analytics
- **Flappy Hedgehog**: Port 8082 - Flappy bird style game

### 3. Watch Real-Time Analytics
Return to the dashboard (port 3000) to see real-time analytics from your gameplay!

## 🔧 Development Commands

Your environment includes helpful aliases:

```bash
# Django shortcuts
dj --help                 # Django manage.py commands
djshell                   # Django shell
djtest                    # Run Django tests
djmigrate                 # Run database migrations

# Project commands  
make start-all            # Start all services
make stop-all             # Stop all services
make test                 # Run all tests
make lint                 # Run linting
make format               # Format code
status                    # Check service status
```

## 📊 Sample Data

The environment comes pre-loaded with:
- ✅ Demo project with API key authentication
- ✅ 100+ sample analytics events
- ✅ Multiple event types (signups, clicks, purchases, etc.)
- ✅ Rich metadata (users, sessions, browsers, etc.)

## 🎮 Analytics Integration Examples

The demo games show real-world analytics patterns:

### Snake Game Events:
- `app_opened` - Game initialization
- `game_started` - New game begun  
- `food_eaten` - Snake eats food (with score)
- `direction_changed` - Snake direction changes
- `game_over` - Game ends (with final score)
- `high_score_achieved` - New high score

### Flappy Hedgehog Events:
- `app_opened` - Game loads
- `game_started` - Game begins
- `hedgehog_flap` - Player input
- `pipe_passed` - Obstacle cleared
- `game_over` - Game ends
- `high_score_achieved` - New record

## 🔍 Explore the Code

Key files to explore:

### Backend (Django)
- `analytics/models.py` - Data models (Project, Event, RateLimit)
- `analytics/views.py` - API endpoints with authentication
- `analytics/serializers.py` - Data validation & serialization
- `analytics/utils.py` - Rate limiting utilities

### Frontend (React)  
- `frontend/src/components/Dashboard.js` - Main analytics dashboard
- `frontend/src/components/EventCapture.js` - Event creation interface
- `frontend/src/config.js` - API configuration

### Demo Games
- `example-apps/snake-game/` - Snake game with analytics
- `example-apps/flappy-hedgehog/` - Flappy bird clone

## 📝 API Testing

Test the API directly using the REST Client extension:

```http
### Get analytics stats
GET http://localhost:8000/api/stats/

### Capture an event
POST http://localhost:8000/api/capture_event/
Content-Type: application/json

{
  "api_key": "pk_...",
  "event_name": "test_event",
  "source": "codespace",
  "properties": {
    "user_id": "dev_user",
    "action": "testing_api"
  }
}
```

## 🎯 Try These Activities

1. **Play the games** - Generate real analytics events
2. **Watch the dashboard** - See real-time updates every 5 seconds
3. **Explore the API** - Test endpoints with different parameters
4. **Modify the code** - Make changes and see them live reload
5. **Run the tests** - Ensure everything works: `make test`
6. **Check code quality** - Run linting: `make lint`

## 🚀 Next Steps

- **Customize the dashboard** - Add new chart types or filters
- **Create new event types** - Add tracking to more user actions  
- **Implement new games** - Create your own demo application
- **Extend the API** - Add new endpoints or authentication methods
- **Scale the database** - Test with larger datasets

## 💡 Tips

- **Auto-refresh**: Dashboard updates every 5 seconds automatically
- **Hot reload**: Frontend changes reload instantly
- **Code formatting**: Save to auto-format with Black/Prettier
- **Debugging**: Use VS Code debugger for Python and JavaScript
- **Logs**: Check `/tmp/*.log` files for service logs

## 🆘 Need Help?

- **Service issues**: Run `make status` to check what's running
- **Restart services**: Use `make stop-all` then `make start-all`
- **Dependencies**: Run `uv sync --dev` to reinstall Python packages
- **Frontend issues**: `cd frontend && npm install` to reinstall Node packages

---

## 🎉 Happy Coding!

You now have a complete analytics platform running in your codespace. Explore, experiment, and build something awesome!

**Star the repo if you found this useful!** ⭐