// Flappy Hedgehog Game with Djangalytics Integration
class FlappyHedgehogGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        // Game dimensions
        this.gravity = 0.4;
        this.jumpStrength = -8;
        this.gameSpeed = 2;
        
        // Hedgehog properties
        this.hedgehog = {
            x: 80,
            y: this.canvas.height / 2,
            width: 30,
            height: 25,
            velocity: 0
        };
        
        // Pipes
        this.pipes = [];
        this.pipeWidth = 50;
        this.pipeGap = 150;
        this.pipeSpacing = 200;
        
        // Game state
        this.score = 0;
        this.highScore = localStorage.getItem('flappyHedgehogHighScore') || 0;
        this.gameRunning = false;
        this.gamePaused = false;
        this.gameStartTime = null;
        this.sessionId = this.generateSessionId();
        this.lastPipeTime = 0;
        
        // Analytics - Load from config
        this.analyticsUrl = `${ANALYTICS_CONFIG.API_BASE_URL}/capture_event/`;
        this.apiKey = ANALYTICS_CONFIG.API_KEY;
        this.gameSource = ANALYTICS_CONFIG.SOURCE_NAME;
        
        // Counters for analytics
        this.flapCount = 0;
        this.collisionCount = 0;
        
        this.init();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    init() {
        document.getElementById('highScore').textContent = this.highScore;
        this.setupEventListeners();
        this.draw();
        
        // Send app started event
        this.sendAnalyticsEvent('app_opened', {
            screen_width: window.screen.width,
            screen_height: window.screen.height,
            user_agent: navigator.userAgent.substring(0, 100),
            canvas_width: this.canvas.width,
            canvas_height: this.canvas.height
        });
    }
    
    setupEventListeners() {
        // Keyboard events
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        
        // Mouse/touch events for flapping
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.handleClick(e);
        });
        
        // Prevent default touch behaviors
        this.canvas.addEventListener('touchmove', (e) => e.preventDefault());
        this.canvas.addEventListener('touchend', (e) => e.preventDefault());
    }
    
    handleKeyPress(e) {
        if (!this.gameRunning && (e.code === 'Space' || e.key === ' ')) {
            this.startGame();
            return;
        }
        
        if (e.code === 'Space' || e.key === ' ') {
            if (this.gameRunning && !this.gamePaused) {
                this.flap();
            }
            e.preventDefault();
        }
        
        if (e.code === 'KeyP' || e.key === 'p' || e.key === 'P') {
            this.togglePause();
        }
        
        if (e.code === 'KeyR' || e.key === 'r' || e.key === 'R') {
            this.resetGame();
        }
    }
    
    handleClick(e) {
        if (!this.gameRunning) {
            this.startGame();
        } else if (!this.gamePaused) {
            this.flap();
        }
    }
    
    flap() {
        this.hedgehog.velocity = this.jumpStrength;
        this.flapCount++;
        
        // Track every flap for analytics
        this.sendAnalyticsEvent('hedgehog_flap', {
            flap_count: this.flapCount,
            hedgehog_y: Math.round(this.hedgehog.y),
            score: this.score,
            velocity: this.hedgehog.velocity,
            game_duration: Date.now() - this.gameStartTime
        });
    }
    
    startGame() {
        if (this.gameRunning) return;
        
        this.gameRunning = true;
        this.gamePaused = false;
        this.gameStartTime = Date.now();
        this.score = 0;
        this.flapCount = 0;
        this.collisionCount = 0;
        this.pipes = [];
        this.lastPipeTime = 0;
        this.hedgehog.y = this.canvas.height / 2;
        this.hedgehog.velocity = 0;
        
        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('score').textContent = '0';
        this.updateStatus('🎮 Playing - Flap to fly!');
        
        this.sendAnalyticsEvent('game_started', {
            hedgehog_start_y: this.hedgehog.y,
            canvas_dimensions: {
                width: this.canvas.width,
                height: this.canvas.height
            }
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
                flap_count: this.flapCount,
                hedgehog_y: this.hedgehog.y,
                game_duration: Date.now() - this.gameStartTime
            });
        } else {
            this.updateStatus('🎮 Playing - Flap to fly!');
            this.sendAnalyticsEvent('game_resumed', {
                score: this.score,
                flap_count: this.flapCount
            });
        }
    }
    
    resetGame() {
        const wasRunning = this.gameRunning;
        const oldScore = this.score;
        const oldFlaps = this.flapCount;
        
        this.gameRunning = false;
        this.gamePaused = false;
        this.score = 0;
        this.flapCount = 0;
        this.collisionCount = 0;
        this.pipes = [];
        this.hedgehog.y = this.canvas.height / 2;
        this.hedgehog.velocity = 0;
        
        document.getElementById('startBtn').style.display = 'inline-block';
        document.getElementById('score').textContent = '0';
        this.updateStatus('Click or Press SPACE to Start');
        this.draw();
        
        if (wasRunning) {
            this.sendAnalyticsEvent('game_reset', {
                old_score: oldScore,
                old_flap_count: oldFlaps,
                game_duration: this.gameStartTime ? Date.now() - this.gameStartTime : 0
            });
        }
    }
    
    gameLoop() {
        if (!this.gameRunning) return;
        
        if (!this.gamePaused) {
            this.update();
        }
        this.draw();
        
        requestAnimationFrame(() => this.gameLoop());
    }
    
    update() {
        // Update hedgehog physics
        this.hedgehog.velocity += this.gravity;
        this.hedgehog.y += this.hedgehog.velocity;
        
        // Generate pipes
        if (Date.now() - this.lastPipeTime > this.pipeSpacing * 10) { // Convert to time-based
            this.createPipe();
            this.lastPipeTime = Date.now();
        }
        
        // Update pipes
        this.pipes.forEach(pipe => {
            pipe.x -= this.gameSpeed;
        });
        
        // Remove off-screen pipes and update score
        const initialPipeCount = this.pipes.length;
        this.pipes = this.pipes.filter(pipe => {
            if (pipe.x + this.pipeWidth < 0) {
                // Pipe passed, increase score
                if (!pipe.scored) {
                    this.score++;
                    document.getElementById('score').textContent = this.score;
                    pipe.scored = true;
                    
                    this.sendAnalyticsEvent('pipe_passed', {
                        score: this.score,
                        pipe_height: pipe.height,
                        hedgehog_y: Math.round(this.hedgehog.y),
                        flap_count: this.flapCount,
                        game_duration: Date.now() - this.gameStartTime
                    });
                    
                    // Check for high score
                    if (this.score > this.highScore) {
                        this.highScore = this.score;
                        localStorage.setItem('flappyHedgehogHighScore', this.highScore);
                        document.getElementById('highScore').textContent = this.highScore;
                        
                        this.sendAnalyticsEvent('high_score_achieved', {
                            new_high_score: this.highScore,
                            flap_count: this.flapCount,
                            game_duration: Date.now() - this.gameStartTime
                        });
                    }
                }
                return false;
            }
            return true;
        });
        
        // Check collisions
        if (this.checkCollisions()) {
            this.gameOver();
        }
    }
    
    createPipe() {
        const minHeight = 50;
        const maxHeight = this.canvas.height - this.pipeGap - minHeight;
        const height = Math.random() * (maxHeight - minHeight) + minHeight;
        
        this.pipes.push({
            x: this.canvas.width,
            y: 0,
            width: this.pipeWidth,
            height: height,
            scored: false
        });
        
        // Bottom pipe
        this.pipes.push({
            x: this.canvas.width,
            y: height + this.pipeGap,
            width: this.pipeWidth,
            height: this.canvas.height - height - this.pipeGap,
            scored: false
        });
    }
    
    checkCollisions() {
        // Check ground and ceiling
        if (this.hedgehog.y <= 0 || this.hedgehog.y + this.hedgehog.height >= this.canvas.height) {
            this.collisionCount++;
            return true;
        }
        
        // Check pipe collisions
        for (let pipe of this.pipes) {
            if (this.hedgehog.x < pipe.x + pipe.width &&
                this.hedgehog.x + this.hedgehog.width > pipe.x &&
                this.hedgehog.y < pipe.y + pipe.height &&
                this.hedgehog.y + this.hedgehog.height > pipe.y) {
                this.collisionCount++;
                return true;
            }
        }
        
        return false;
    }
    
    gameOver() {
        this.gameRunning = false;
        this.updateStatus('💀 Game Over! Click to restart');
        document.getElementById('startBtn').style.display = 'inline-block';
        
        const gameDuration = Date.now() - this.gameStartTime;
        const averageFlapsPerSecond = this.flapCount / (gameDuration / 1000);
        const survivalRate = this.score / Math.max(this.flapCount, 1);
        
        this.sendAnalyticsEvent('game_over', {
            final_score: this.score,
            high_score: this.highScore,
            total_flaps: this.flapCount,
            collision_count: this.collisionCount,
            game_duration: gameDuration,
            pipes_passed: this.score,
            average_flaps_per_second: averageFlapsPerSecond,
            survival_rate: survivalRate,
            final_hedgehog_y: Math.round(this.hedgehog.y),
            cause_of_death: this.hedgehog.y <= 0 ? 'ceiling' : 
                           this.hedgehog.y + this.hedgehog.height >= this.canvas.height ? 'ground' : 'pipe'
        });
    }
    
    draw() {
        // Clear canvas - terminal black background
        this.ctx.fillStyle = '#000000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw terminal-style grid pattern (very subtle)
        this.ctx.strokeStyle = '#001111';
        this.ctx.lineWidth = 0.5;
        for (let i = 0; i < this.canvas.width; i += 20) {
            this.ctx.beginPath();
            this.ctx.moveTo(i, 0);
            this.ctx.lineTo(i, this.canvas.height);
            this.ctx.stroke();
        }
        
        // Draw pipes - terminal cyan blocks
        this.ctx.fillStyle = '#00FFFF';
        this.pipes.forEach(pipe => {
            this.ctx.fillRect(pipe.x, pipe.y, pipe.width, pipe.height);
            
            // Pipe border for terminal effect
            this.ctx.strokeStyle = '#0088AA';
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(pipe.x, pipe.y, pipe.width, pipe.height);
            
            // Inner pattern
            this.ctx.fillStyle = '#0088AA';
            for (let i = pipe.y; i < pipe.y + pipe.height; i += 8) {
                this.ctx.fillRect(pipe.x + 2, i, pipe.width - 4, 2);
            }
            this.ctx.fillStyle = '#00FFFF';
        });
        
        // Draw hedgehog
        this.drawHedgehog();
        
        // Draw ground - terminal style
        this.ctx.fillStyle = '#00FFFF';
        this.ctx.fillRect(0, this.canvas.height - 10, this.canvas.width, 10);
        this.ctx.strokeStyle = '#0088AA';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(0, this.canvas.height - 10, this.canvas.width, 10);
    }
    
    drawClouds() {
        // No clouds in terminal mode - keep function for compatibility
    }
    
    drawHedgehog() {
        const x = this.hedgehog.x;
        const y = this.hedgehog.y;
        const w = this.hedgehog.width;
        const h = this.hedgehog.height;
        
        // Hedgehog body - terminal cyan block
        this.ctx.fillStyle = '#00FFFF';
        this.ctx.fillRect(x + 2, y + 2, w - 4, h - 4);
        
        // Body border
        this.ctx.strokeStyle = '#0088AA';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(x + 2, y + 2, w - 4, h - 4);
        
        // Simple terminal "spikes" - just rectangular blocks
        this.ctx.fillStyle = '#00AAAA';
        for (let i = 0; i < 3; i++) {
            const spikeX = x + (i * 6) + 6;
            const spikeY = y - 2;
            this.ctx.fillRect(spikeX, spikeY, 4, 6);
        }
        
        // Simple "face" - just a smaller block
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.fillRect(x + w - 8, y + 4, 6, 6);
        
        // "Eye" - tiny black square
        this.ctx.fillStyle = '#000000';
        this.ctx.fillRect(x + w - 6, y + 5, 2, 2);
        
        // Eye highlight
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.beginPath();
        this.ctx.arc(x + w/2 + 9, y + h/2 - 4, 1, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Nose
        this.ctx.fillStyle = '#000000';
        this.ctx.beginPath();
        this.ctx.arc(x + w/2 + 12, y + h/2, 1, 0, Math.PI * 2);
        this.ctx.fill();
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
        if (properties.final_score !== undefined) keyProps.push(`final=${properties.final_score}`);
        if (properties.flap_count !== undefined) keyProps.push(`flaps=${properties.flap_count}`);
        if (properties.total_flaps !== undefined) keyProps.push(`total_flaps=${properties.total_flaps}`);
        if (properties.new_high_score !== undefined) keyProps.push(`highscore=${properties.new_high_score}`);
        if (properties.collision_type !== undefined) keyProps.push(`hit=${properties.collision_type}`);
        if (properties.pipe_height !== undefined) keyProps.push(`pipe_h=${properties.pipe_height}`);
        
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
    game = new FlappyHedgehogGame();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (game && game.gameRunning && !game.gamePaused && document.hidden) {
        game.sendAnalyticsEvent('tab_hidden', {
            score: game.score,
            flap_count: game.flapCount,
            hedgehog_y: Math.round(game.hedgehog.y)
        });
    } else if (game && game.gameRunning && !document.hidden) {
        game.sendAnalyticsEvent('tab_visible', {
            score: game.score,
            flap_count: game.flapCount,
            hedgehog_y: Math.round(game.hedgehog.y)
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
                flap_count: game.flapCount,
                hedgehog_y: Math.round(game.hedgehog.y),
                game_duration: game.gameStartTime ? Date.now() - game.gameStartTime : 0
            }
        };
        
        navigator.sendBeacon(game.analyticsUrl, JSON.stringify(event));
    }
});