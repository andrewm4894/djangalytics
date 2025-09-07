import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState({
    daily_stats: [],
    event_counts: [],
    source_counts: [],
    recent_events: [],
    total_events: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const colors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

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
    try {
      setError(null);
      const response = await axios.get('http://localhost:8000/api/stats/');
      setStats(response.data);
    } catch (error) {
      setError('Failed to fetch analytics data: ' + (error.response?.data?.detail || error.message));
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  // Transform daily stats for line chart
  const dailyChartData = stats.daily_stats.reduce((acc, curr) => {
    const existing = acc.find(item => item.date === curr.date);
    if (existing) {
      existing[curr.event_name] = curr.count;
      existing.total = (existing.total || 0) + curr.count;
    } else {
      acc.push({
        date: curr.date,
        [curr.event_name]: curr.count,
        total: curr.count
      });
    }
    return acc;
  }, []).sort((a, b) => new Date(a.date) - new Date(b.date));

  // Transform event counts for pie chart
  const pieChartData = stats.event_counts.map((item, index) => ({
    name: item.event_name,
    value: item.count,
    fill: colors[index % colors.length]
  }));

  if (loading) {
    return <div className="loading">Loading analytics data...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Analytics Dashboard</h2>
        <div className="total-events">
          Total Events: <strong>{stats.total_events}</strong>
        </div>
        <button onClick={fetchStats} className="refresh-btn">
          Refresh Data
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="charts-container">
        {/* Event Counts Bar Chart */}
        <div className="chart-section">
          <h3>Event Types Distribution</h3>
          {stats.event_counts.length > 0 ? (
            <BarChart width={500} height={300} data={stats.event_counts}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="event_name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          ) : (
            <p>No event data available</p>
          )}
        </div>

        {/* Daily Trends Line Chart */}
        <div className="chart-section">
          <h3>Daily Event Trends (Last 7 Days)</h3>
          {dailyChartData.length > 0 ? (
            <LineChart width={500} height={300} data={dailyChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="total" stroke="#8884d8" />
            </LineChart>
          ) : (
            <p>No daily trend data available</p>
          )}
        </div>

        {/* Event Types Pie Chart */}
        <div className="chart-section">
          <h3>Event Types Breakdown</h3>
          {pieChartData.length > 0 ? (
            <PieChart width={400} height={300}>
              <Pie
                data={pieChartData}
                cx={200}
                cy={150}
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          ) : (
            <p>No event breakdown data available</p>
          )}
        </div>

        {/* Event Sources Bar Chart */}
        <div className="chart-section">
          <h3>Events by Source</h3>
          {stats.source_counts && stats.source_counts.length > 0 ? (
            <BarChart width={500} height={300} data={stats.source_counts}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="source" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#00C49F" />
            </BarChart>
          ) : (
            <p>No source data available</p>
          )}
        </div>
      </div>

      {/* Live Feed */}
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
    </div>
  );
};

export default Dashboard;