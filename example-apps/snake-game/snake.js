// Snake Game with Djangalytics Integration
class SnakeGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 20;
        this.tileCount = this.canvas.width / this.gridSize;
        
        // Game state
        this.snake = [{ x: 10, y: 10 }];
        this.food = {};
        this.direction = { x: 0, y: 0 };
        this.score = 0;
        this.highScore = localStorage.getItem('snakeHighScore') || 0;
        this.gameRunning = false;
        this.gamePaused = false;
        this.gameStartTime = null;
        this.sessionId = this.generateSessionId();
        
        // Analytics - Load from config
        this.analyticsUrl = `${ANALYTICS_CONFIG.API_BASE_URL}/capture_event/`;
        this.apiKey = ANALYTICS_CONFIG.API_KEY;
        this.gameSource = ANALYTICS_CONFIG.SOURCE_NAME;
        
        this.init();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    init() {
        document.getElementById('highScore').textContent = this.highScore;
        this.setupEventListeners();
        this.placeFood();
        this.draw();
        
        // Send app started event
        this.sendAnalyticsEvent('app_opened', {
            screen_width: window.screen.width,
            screen_height: window.screen.height,
            user_agent: navigator.userAgent.substring(0, 100)
        });
    }
    
    setupEventListeners() {
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        
        // Prevent page scroll with arrow keys
        document.addEventListener('keydown', (e) => {
            if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) {
                e.preventDefault();
            }
        });
    }
    
    handleKeyPress(e) {
        if (!this.gameRunning && e.code === 'Space') {
            this.startGame();
            return;
        }
        
        if (!this.gameRunning) return;
        
        const keyMap = {
            'ArrowUp': { x: 0, y: -1 },
            'ArrowDown': { x: 0, y: 1 },
            'ArrowLeft': { x: -1, y: 0 },
            'ArrowRight': { x: 1, y: 0 },
            'KeyW': { x: 0, y: -1 },
            'KeyS': { x: 0, y: 1 },
            'KeyA': { x: -1, y: 0 },
            'KeyD': { x: 1, y: 0 },
        };
        
        if (keyMap[e.code]) {
            const newDirection = keyMap[e.code];
            // Prevent reversing into itself
            if (newDirection.x !== -this.direction.x || newDirection.y !== -this.direction.y) {
                this.direction = newDirection;
                
                // Track all direction changes for analytics
                this.sendAnalyticsEvent('direction_changed', {
                    new_direction: this.getDirectionName(newDirection),
                    score: this.score,
                    snake_length: this.snake.length
                });
            }
        }
        
        if (e.code === 'Space') {
            this.togglePause();
        }
        
        if (e.code === 'KeyR') {
            this.resetGame();
        }
    }
    
    getDirectionName(dir) {
        if (dir.x === 1) return 'right';
        if (dir.x === -1) return 'left';
        if (dir.y === 1) return 'down';
        if (dir.y === -1) return 'up';
        return 'none';
    }
    
    startGame() {
        if (this.gameRunning) return;
        
        this.gameRunning = true;
        this.gamePaused = false;
        this.gameStartTime = Date.now();
        this.direction = { x: 1, y: 0 }; // Start moving right
        
        document.getElementById('startBtn').style.display = 'none';
        this.updateStatus('🎮 Playing');
        
        this.sendAnalyticsEvent('game_started', {
            snake_length: this.snake.length,
            current_score: this.score,
            high_score: this.highScore
        });
        
        this.gameLoop();
    }
    
    togglePause() {
        if (!this.gameRunning) return;
        
        this.gamePaused = !this.gamePaused;
        
        if (this.gamePaused) {
            this.updateStatus('⏸️ Paused');
            this.sendAnalyticsEvent('game_paused', {
                score: this.score,
                snake_length: this.snake.length,
                game_duration: Date.now() - this.gameStartTime
            });
        } else {
            this.updateStatus('🎮 Playing');
            this.sendAnalyticsEvent('game_resumed', {
                score: this.score,
                snake_length: this.snake.length
            });
        }
    }
    
    resetGame() {
        const wasRunning = this.gameRunning;
        const oldScore = this.score;
        
        this.gameRunning = false;
        this.gamePaused = false;
        this.snake = [{ x: 10, y: 10 }];
        this.direction = { x: 0, y: 0 };
        this.score = 0;
        this.placeFood();
        this.draw();
        
        document.getElementById('startBtn').style.display = 'inline-block';
        document.getElementById('score').textContent = '0';
        this.updateStatus('Press SPACE to Start');
        
        if (wasRunning) {
            this.sendAnalyticsEvent('game_reset', {
                old_score: oldScore,
                snake_length: this.snake.length,
                game_duration: this.gameStartTime ? Date.now() - this.gameStartTime : 0
            });
        }
    }
    
    gameLoop() {
        if (!this.gameRunning) return;
        
        if (!this.gamePaused) {
            this.update();
            this.draw();
        }
        
        setTimeout(() => this.gameLoop(), 120); // Game speed
    }
    
    update() {
        const head = { x: this.snake[0].x + this.direction.x, y: this.snake[0].y + this.direction.y };
        
        // Check wall collision
        if (head.x < 0 || head.x >= this.tileCount || head.y < 0 || head.y >= this.tileCount) {
            this.gameOver();
            return;
        }
        
        // Check self collision
        if (this.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
            this.gameOver();
            return;
        }
        
        this.snake.unshift(head);
        
        // Check food collision
        if (head.x === this.food.x && head.y === this.food.y) {
            this.score += 10;
            document.getElementById('score').textContent = this.score;
            
            this.sendAnalyticsEvent('food_eaten', {
                score: this.score,
                snake_length: this.snake.length,
                food_position: { x: this.food.x, y: this.food.y },
                game_duration: Date.now() - this.gameStartTime
            });
            
            this.placeFood();
            
            // Check for high score
            if (this.score > this.highScore) {
                this.highScore = this.score;
                localStorage.setItem('snakeHighScore', this.highScore);
                document.getElementById('highScore').textContent = this.highScore;
                
                this.sendAnalyticsEvent('high_score_achieved', {
                    new_high_score: this.highScore,
                    previous_high_score: localStorage.getItem('snakeHighScore') || 0,
                    snake_length: this.snake.length,
                    game_duration: Date.now() - this.gameStartTime
                });
            }
        } else {
            this.snake.pop();
        }
    }
    
    gameOver() {
        this.gameRunning = false;
        this.updateStatus('💀 Game Over!');
        document.getElementById('startBtn').style.display = 'inline-block';
        
        const gameDuration = Date.now() - this.gameStartTime;
        
        this.sendAnalyticsEvent('game_over', {
            final_score: this.score,
            high_score: this.highScore,
            snake_length: this.snake.length,
            game_duration: gameDuration,
            food_eaten: this.score / 10, // Each food is 10 points
            average_score_per_second: this.score / (gameDuration / 1000)
        });
    }
    
    placeFood() {
        do {
            this.food = {
                x: Math.floor(Math.random() * this.tileCount),
                y: Math.floor(Math.random() * this.tileCount)
            };
        } while (this.snake.some(segment => segment.x === this.food.x && segment.y === this.food.y));
    }
    
    draw() {
        // Clear canvas - terminal black background
        this.ctx.fillStyle = '#000000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw terminal-style grid (optional faint grid lines)
        this.ctx.strokeStyle = '#002200';
        this.ctx.lineWidth = 0.5;
        for (let i = 0; i <= this.tileCount; i++) {
            // Vertical lines
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.gridSize, 0);
            this.ctx.lineTo(i * this.gridSize, this.canvas.height);
            this.ctx.stroke();
            
            // Horizontal lines
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.gridSize);
            this.ctx.lineTo(this.canvas.width, i * this.gridSize);
            this.ctx.stroke();
        }
        
        // Draw snake - terminal green
        this.snake.forEach((segment, index) => {
            if (index === 0) {
                // Head - bright terminal green with border
                this.ctx.fillStyle = '#00FF00';
                this.ctx.fillRect(segment.x * this.gridSize + 1, segment.y * this.gridSize + 1, this.gridSize - 2, this.gridSize - 2);
                // Head border
                this.ctx.strokeStyle = '#00AA00';
                this.ctx.lineWidth = 1;
                this.ctx.strokeRect(segment.x * this.gridSize + 1, segment.y * this.gridSize + 1, this.gridSize - 2, this.gridSize - 2);
            } else {
                // Body - dimmer green blocks
                this.ctx.fillStyle = '#00AA00';
                this.ctx.fillRect(segment.x * this.gridSize + 2, segment.y * this.gridSize + 2, this.gridSize - 4, this.gridSize - 4);
            }
        });
        
        // Draw food - terminal style
        this.ctx.fillStyle = '#00FF00';
        this.ctx.fillRect(this.food.x * this.gridSize + 3, this.food.y * this.gridSize + 3, this.gridSize - 6, this.gridSize - 6);
        
        // Food border/indicator
        this.ctx.strokeStyle = '#00FF00';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(this.food.x * this.gridSize + 1, this.food.y * this.gridSize + 1, this.gridSize - 2, this.gridSize - 2);
    }
    
    updateStatus(text) {
        const statusEl = document.getElementById('gameStatus');
        statusEl.textContent = text;
        
        // Update status class
        statusEl.className = 'status';
        if (text.includes('Game Over')) {
            statusEl.classList.add('game-over');
        } else if (text.includes('Playing')) {
            statusEl.classList.add('playing');
        } else if (text.includes('Paused')) {
            statusEl.classList.add('paused');
        }
    }
    
    async sendAnalyticsEvent(eventName, properties = {}) {
        const event = {
            event_name: eventName,
            source: this.gameSource,
            api_key: this.apiKey,
            properties: {
                session_id: this.sessionId,
                timestamp: new Date().toISOString(),
                ...properties
            }
        };
        
        // Log to telemetry display
        this.logEventToDisplay(eventName, properties);
        
        try {
            const response = await fetch(this.analyticsUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(event)
            });
            
            if (response.ok) {
                this.updateAnalyticsStatus('✅ Analytics Connected', 'analytics-success');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Analytics error:', error);
            this.updateAnalyticsStatus('❌ Analytics Error', 'analytics-error');
        }
    }
    
    logEventToDisplay(eventName, properties = {}) {
        const logElement = document.getElementById('eventLog');
        const timestamp = new Date().toISOString().substring(11, 19); // HH:MM:SS
        
        // Create log entry
        let logEntry = `${timestamp} > ${eventName.toUpperCase()}`;
        
        // Add key properties
        const keyProps = [];
        if (properties.score !== undefined) keyProps.push(`score=${properties.score}`);
        if (properties.snake_length !== undefined) keyProps.push(`len=${properties.snake_length}`);
        if (properties.final_score !== undefined) keyProps.push(`final=${properties.final_score}`);
        if (properties.new_direction !== undefined) keyProps.push(`dir=${properties.new_direction}`);
        if (properties.food_eaten !== undefined) keyProps.push(`eaten=${properties.food_eaten}`);
        if (properties.new_high_score !== undefined) keyProps.push(`highscore=${properties.new_high_score}`);
        
        if (keyProps.length > 0) {
            logEntry += ` [${keyProps.join(', ')}]`;
        }
        
        // Clear "AWAITING EVENTS..." on first event
        if (logElement.innerHTML.includes('AWAITING EVENTS')) {
            logElement.innerHTML = '';
        }
        
        // Add new entry
        logElement.innerHTML += logEntry + '<br>';
        
        // Keep only last 20 entries
        const lines = logElement.innerHTML.split('<br>').filter(line => line.trim());
        if (lines.length > 20) {
            logElement.innerHTML = lines.slice(-20).join('<br>') + '<br>';
        }
        
        // Auto-scroll to bottom
        logElement.scrollTop = logElement.scrollHeight;
    }
    
    updateAnalyticsStatus(message, className) {
        const statusEl = document.getElementById('analyticsStatus');
        statusEl.textContent = message;
        statusEl.className = `analytics-status ${className}`;
        
        // Reset to default after 3 seconds
        setTimeout(() => {
            statusEl.textContent = 'Analytics: Ready';
            statusEl.className = 'analytics-status';
        }, 3000);
    }
}

// Global functions for buttons
let game;

function startGame() {
    game.startGame();
}

function togglePause() {
    game.togglePause();
}

function resetGame() {
    game.resetGame();
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    game = new SnakeGame();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (game && game.gameRunning && !game.gamePaused && document.hidden) {
        game.sendAnalyticsEvent('tab_hidden', {
            score: game.score,
            snake_length: game.snake.length
        });
    } else if (game && game.gameRunning && !document.hidden) {
        game.sendAnalyticsEvent('tab_visible', {
            score: game.score,
            snake_length: game.snake.length
        });
    }
});

// Send analytics when user leaves the page
window.addEventListener('beforeunload', () => {
    if (game && game.gameRunning) {
        // Use sendBeacon for reliable analytics on page unload
        const event = {
            event_name: 'page_unload',
            source: game.gameSource,
            api_key: game.apiKey,
            properties: {
                session_id: game.sessionId,
                score: game.score,
                snake_length: game.snake.length,
                game_duration: game.gameStartTime ? Date.now() - game.gameStartTime : 0
            }
        };
        
        navigator.sendBeacon(game.analyticsUrl, JSON.stringify(event));
    }
});