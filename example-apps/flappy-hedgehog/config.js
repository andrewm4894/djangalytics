/**
 * Flappy Hedgehog Game Analytics Configuration
 */
const ANALYTICS_CONFIG = {
    API_BASE_URL: 'http://localhost:8000/api',
    API_KEY: 'pk_flappy_demo_key_12345678901234567890123',
    SOURCE_NAME: 'flappy-hedgehog',
    
    // Sampling rate for high-frequency events (0.0 to 1.0)
    SAMPLE_RATE: 1.0, // Track all flap events
    
    // Debug mode
    DEBUG: false
};

// Make available globally
window.ANALYTICS_CONFIG = ANALYTICS_CONFIG;