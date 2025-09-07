#!/bin/bash
set -e

echo "🚀 Starting Djangalytics services..."

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start a service in the background
start_service() {
    local name=$1
    local command=$2
    local port=$3
    local log_file="/tmp/${name}.log"
    
    if check_port $port; then
        echo "✅ $name already running on port $port"
        return
    fi
    
    echo "🔄 Starting $name on port $port..."
    nohup bash -c "$command" > "$log_file" 2>&1 &
    local pid=$!
    
    # Wait a bit and check if the service started successfully
    sleep 3
    if kill -0 $pid 2>/dev/null; then
        echo "✅ $name started successfully (PID: $pid)"
        echo "   Log file: $log_file"
    else
        echo "❌ Failed to start $name. Check log: $log_file"
    fi
}

# Start Django backend
start_service "Django Backend" "cd /workspaces/djangalytics && uv run python manage.py runserver 0.0.0.0:8000" 8000

# Start React frontend  
start_service "React Frontend" "cd /workspaces/djangalytics/frontend && npm start" 3000

# Start Snake game
start_service "Snake Game" "cd /workspaces/djangalytics/example-apps/snake-game && python -m http.server 8081" 8081

# Start Flappy Hedgehog game
start_service "Flappy Hedgehog" "cd /workspaces/djangalytics/example-apps/flappy-hedgehog && python -m http.server 8082" 8082

echo ""
echo "🎉 All services are starting up!"
echo ""
echo "📍 Service URLs:"
echo "   • Django Backend:    http://localhost:8000"
echo "   • React Dashboard:   http://localhost:3000"
echo "   • Snake Game:        http://localhost:8081"
echo "   • Flappy Hedgehog:   http://localhost:8082"
echo ""
echo "⏳ Services may take a few moments to fully initialize..."
echo "🔍 Use 'make status' to check if all services are running"
echo "🛑 Use 'make stop-all' to stop all services"