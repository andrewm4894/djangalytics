import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line } from 'recharts';

const Dashboard = ({ selectedProject }) => {
  const [stats, setStats] = useState({
    daily_stats: [],
    event_counts: [],
    source_counts: [],
    recent_events: [],
    total_events: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeWindow, setTimeWindow] = useState(() => {
    return localStorage.getItem('dashboardTimeWindow') || '24h';
  });
  const [freq, setFreq] = useState(() => {
    return localStorage.getItem('dashboardFreq') || '5m';
  });

  const colors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Handle time window and frequency changes with localStorage persistence
  const handleTimeWindowChange = (newTimeWindow) => {
    setTimeWindow(newTimeWindow);
    localStorage.setItem('dashboardTimeWindow', newTimeWindow);
  };

  const handleFreqChange = (newFreq) => {
    setFreq(newFreq);
    localStorage.setItem('dashboardFreq', newFreq);
  };

  // Helper functions for event formatting
  const getEventIcon = (eventName) => {
    const iconMap = {
      'app_opened': '🚀',
      'game_started': '🎮',
      'game_over': '💀',
      'game_reset': '🔄',
      'food_eaten': '🍎',
      'direction_changed': '↗️',
      'hedgehog_flap': '🪶',
      'pipe_passed': '🏆',
      'high_score_achieved': '👑',
      'game_paused': '⏸️',
      'game_resumed': '▶️',
      'tab_hidden': '👁️‍🗨️',
      'tab_visible': '👁️',
      'page_unload': '🚪'
    };
    return iconMap[eventName] || '📊';
  };

  const getSourceIcon = (source) => {
    const iconMap = {
      'snake-game': '🐍',
      'flappy-hedgehog': '🦔',
      'web': '🌐'
    };
    return iconMap[source] || '🌐';
  };

  const formatEventName = (eventName) => {
    return eventName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const eventTime = new Date(timestamp);
    const diffMs = now - eventTime;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);

    if (diffSecs < 60) return `${diffSecs}s ago`;
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  const formatProperties = (properties) => {
    const important = ['score', 'flap_count', 'snake_length', 'game_duration'];
    const formatted = [];
    
    // Show important properties first
    important.forEach(key => {
      if (properties[key] !== undefined) {
        formatted.push(`${key}: ${properties[key]}`);
      }
    });
    
    // Add other properties (limit to 3 total)
    Object.keys(properties).forEach(key => {
      if (!important.includes(key) && formatted.length < 3) {
        let value = properties[key];
        if (typeof value === 'object') {
          value = JSON.stringify(value);
        }
        formatted.push(`${key}: ${value}`);
      }
    });
    
    return formatted.join(' • ');
  };

  const fetchStats = async () => {
    if (!selectedProject) return;
    
    try {
      setError(null);
      const response = await axios.get(`http://localhost:8000/api/stats/?api_key=${selectedProject.api_key}&time_window=${timeWindow}&freq=${freq}`);
      setStats(response.data);
    } catch (error) {
      setError('Failed to fetch analytics data: ' + (error.response?.data?.detail || error.message));
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProject) {
      setLoading(true);
      fetchStats();
      
      // Auto-refresh every 5 seconds
      const interval = setInterval(fetchStats, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedProject, timeWindow, freq]); // eslint-disable-line react-hooks/exhaustive-deps

  // Transform stats for time series chart - group by time bucket
  const timeSeriesData = stats.daily_stats.reduce((acc, curr) => {
    const timeKey = curr.time_bucket || curr.date; // Fallback to date for compatibility
    const existing = acc.find(item => item.time === timeKey);
    if (existing) {
      existing[curr.event_name] = curr.count;
      existing.total = (existing.total || 0) + curr.count;
    } else {
      acc.push({
        time: timeKey,
        [curr.event_name]: curr.count,
        total: curr.count
      });
    }
    return acc;
  }, []).sort((a, b) => new Date(a.time) - new Date(b.time));

  // Get unique event types for line colors
  const eventTypes = [...new Set(stats.daily_stats.map(item => item.event_name))];

  if (loading) {
    return <div className="loading">Loading analytics data for {selectedProject?.name}...</div>;
  }

  const hasData = stats.total_events > 0;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Analytics Dashboard - {selectedProject?.name}</h2>
        <div className="dashboard-controls">
          <div className="control-group">
            <label htmlFor="timeWindow">Time Window:</label>
            <select 
              id="timeWindow" 
              value={timeWindow} 
              onChange={(e) => handleTimeWindowChange(e.target.value)}
              className="control-select"
            >
              <option value="1h">Last Hour</option>
              <option value="6h">Last 6 Hours</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>
          
          <div className="control-group">
            <label htmlFor="freq">Frequency:</label>
            <select 
              id="freq" 
              value={freq} 
              onChange={(e) => handleFreqChange(e.target.value)}
              className="control-select"
            >
              <option value="1m">1 Minute</option>
              <option value="5m">5 Minutes</option>
              <option value="15m">15 Minutes</option>
              <option value="1h">1 Hour</option>
              <option value="1d">1 Day</option>
            </select>
          </div>
          
          <div className="total-events">
            Total Events: <strong>{stats.total_events}</strong>
          </div>
          
          <button onClick={fetchStats} className="refresh-btn">
            Refresh Data
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {!hasData && (
        <div className="empty-state">
          <div className="empty-state-icon">📊</div>
          <h3>No Analytics Data Yet</h3>
          <p>This project hasn't received any events yet.</p>
          <p className="empty-state-subtitle">
            Start sending events from your applications to see analytics data here.
          </p>
        </div>
      )}

      {hasData && (
        <div className="chart-container">
          <div className="chart-section">
            <h3>Event Timeline</h3>
            {timeSeriesData.length > 0 ? (
              <LineChart width={1100} height={400} data={timeSeriesData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="time" 
                  stroke="#666"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#666"
                  fontSize={12}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                />
                <Legend />
                {eventTypes.map((eventType, index) => (
                  <Line 
                    key={eventType}
                    type="monotone" 
                    dataKey={eventType} 
                    stroke={colors[index % colors.length]}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                ))}
              </LineChart>
            ) : (
              <div className="no-chart-data">
                <p>No time series data available yet</p>
                <p className="no-chart-subtitle">Events will appear here as they are received</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Live Feed */}
      {hasData && (
        <div className="live-feed">
        <div className="live-feed-header">
          <h3>🔴 Live Events Feed</h3>
          <div className="event-count-badge">
            {stats.recent_events.length} recent events
          </div>
        </div>
        
        <div className="events-table-container">
          {stats.recent_events.length > 0 ? (
            <div className="events-table">
              <div className="events-table-header">
                <div className="col-event">Event</div>
                <div className="col-source">Source</div>
                <div className="col-time">Time</div>
                <div className="col-details">Details</div>
              </div>
              
              <div className="events-table-body">
                {stats.recent_events.map(event => (
                  <div key={event.id} className="event-row">
                    <div className="col-event">
                      <span className={`event-type-badge ${event.event_name.replace(/_/g, '-')}`}>
                        {getEventIcon(event.event_name)}
                      </span>
                      <span className="event-name">{formatEventName(event.event_name)}</span>
                    </div>
                    
                    <div className="col-source">
                      <span className={`source-badge ${event.source || 'web'}`}>
                        {getSourceIcon(event.source)} {event.source || 'web'}
                      </span>
                    </div>
                    
                    <div className="col-time">
                      <span className="time-main">
                        {formatTime(event.timestamp)}
                      </span>
                      <span className="time-ago">
                        {getTimeAgo(event.timestamp)}
                      </span>
                    </div>
                    
                    <div className="col-details">
                      {event.properties && Object.keys(event.properties).length > 0 ? (
                        <div className="event-properties">
                          {formatProperties(event.properties)}
                        </div>
                      ) : (
                        <span className="no-details">—</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="no-events">
              <div className="no-events-icon">📊</div>
              <p>No recent events</p>
              <p className="no-events-subtitle">Start playing the games to see events appear here!</p>
            </div>
          )}
        </div>
      </div>
      )}
    </div>
  );
};

export default Dashboard;