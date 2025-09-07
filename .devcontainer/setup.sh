#!/bin/bash
set -e

echo "🚀 Setting up Djangalytics Development Environment..."

# Update system packages
sudo apt-get update

# Install additional system dependencies
sudo apt-get install -y \
    sqlite3 \
    tree \
    htop \
    curl \
    wget \
    jq

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install Python dependencies with uv
echo "🐍 Installing Python dependencies..."
uv sync --dev

# Install Node.js dependencies for frontend
echo "⚛️ Installing Node.js dependencies..."
cd frontend && npm install && cd ..

# Set up the database
echo "🗄️ Setting up database..."
uv run python manage.py migrate

# Create a demo project and generate sample data
echo "🌱 Creating sample data..."
uv run python -c "
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangalytics.settings')
django.setup()

from analytics.models import Project, Event
from django.utils import timezone
import random
from datetime import timedelta

# Create demo project if it doesn't exist
project, created = Project.objects.get_or_create(
    name='Demo Project',
    defaults={'slug': 'demo-project'}
)

if created:
    print(f'✅ Created demo project with API key: {project.api_key}')
else:
    print(f'✅ Using existing demo project with API key: {project.api_key}')

# Generate sample events if none exist
if Event.objects.count() < 50:
    print('📊 Generating sample analytics events...')
    
    event_types = ['user_signup', 'page_view', 'button_click', 'form_submit', 'purchase', 'logout']
    sources = ['web', 'mobile', 'tablet']
    
    events = []
    for i in range(100):
        timestamp = timezone.now() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        events.append(Event(
            project=project,
            event_name=random.choice(event_types),
            source=random.choice(sources),
            timestamp=timestamp,
            properties={
                'user_id': f'user_{random.randint(1, 50)}',
                'session_id': f'session_{random.randint(1, 20)}',
                'value': random.randint(1, 1000),
                'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                'os': random.choice(['Windows', 'macOS', 'Linux', 'iOS', 'Android'])
            }
        ))
    
    Event.objects.bulk_create(events)
    print(f'✅ Created {len(events)} sample events')
else:
    print('✅ Sample data already exists')

print(f'🎯 Demo project API key: {project.api_key}')
"

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
uv run pre-commit install

# Create a .env file for development
echo "📝 Creating development environment file..."
cat > .env << EOL
# Development Environment Variables
DEBUG=True
ALLOWED_HOSTS=*,localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Demo project info (created during setup)
DEMO_API_KEY=\$(uv run python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangalytics.settings'); django.setup(); from analytics.models import Project; print(Project.objects.first().api_key)")
EOL

# Create useful aliases
echo "⚙️ Setting up development aliases..."
cat >> ~/.bashrc << 'EOL'

# Djangalytics development aliases
alias dj="uv run python manage.py"
alias djshell="uv run python manage.py shell"
alias djtest="uv run python manage.py test analytics"
alias djmigrate="uv run python manage.py migrate"
alias djserver="uv run python manage.py runserver"
alias npmfrontend="cd frontend && npm"
alias startall="make start-all"
alias stopall="make stop-all"
alias lintall="make lint"
alias formatall="make format"

# Show project status
alias status="make status"
EOL

# Make scripts executable
chmod +x .devcontainer/*.sh

echo ""
echo "🎉 Setup complete! Your Djangalytics development environment is ready!"
echo ""
echo "📍 Available services:"
echo "   • Django Backend: http://localhost:8000"
echo "   • React Frontend: http://localhost:3000"  
echo "   • Snake Game: http://localhost:8081"
echo "   • Flappy Hedgehog: http://localhost:8082"
echo ""
echo "🔧 Quick commands:"
echo "   • make start-all    - Start all services"
echo "   • make test         - Run all tests"
echo "   • make lint         - Run linting"
echo "   • djshell           - Django shell"
echo "   • status            - Check service status"
echo ""
echo "📖 Check out welcome.md for more information!"