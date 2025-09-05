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
        <h3>Recent Events Feed</h3>
        <div className="events-list">
          {stats.recent_events.length > 0 ? (
            stats.recent_events.map(event => (
              <div key={event.id} className="event-item">
                <span className="event-name">{event.event_name}</span>
                <span className="event-source">
                  [{event.source || 'web'}]
                </span>
                <span className="event-time">
                  {new Date(event.timestamp).toLocaleString()}
                </span>
                {event.properties && Object.keys(event.properties).length > 0 && (
                  <span className="event-properties">
                    {JSON.stringify(event.properties)}
                  </span>
                )}
              </div>
            ))
          ) : (
            <p>No recent events</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;