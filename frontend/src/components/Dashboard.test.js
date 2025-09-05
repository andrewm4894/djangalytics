import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from './Dashboard';

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn()
}));

// Mock Recharts components to avoid rendering issues in tests
jest.mock('recharts', () => ({
  BarChart: ({ children }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  LineChart: ({ children }) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  PieChart: ({ children }) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />,
}));

const mockStatsData = {
  daily_stats: [
    { date: '2024-01-01', event_name: 'user_signup', count: 5 },
    { date: '2024-01-01', event_name: 'page_view', count: 20 },
    { date: '2024-01-02', event_name: 'user_signup', count: 3 },
  ],
  event_counts: [
    { event_name: 'page_view', count: 25 },
    { event_name: 'user_signup', count: 8 },
    { event_name: 'button_click', count: 15 },
  ],
  recent_events: [
    {
      id: 1,
      event_name: 'user_signup',
      timestamp: '2024-01-01T12:00:00Z',
      properties: { user_id: 123 }
    },
    {
      id: 2,
      event_name: 'page_view',
      timestamp: '2024-01-01T11:30:00Z',
      properties: {}
    },
  ],
  total_events: 48
};

import axios from 'axios';

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock successful API response by default
    axios.get.mockResolvedValue({ data: mockStatsData });
  });

  afterEach(() => {
    // Clear any existing intervals
    jest.clearAllTimers();
  });

  test('renders dashboard header', async () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Total Events: 48')).toBeInTheDocument();
    });
  });

  test('renders refresh button', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Refresh Data')).toBeInTheDocument();
  });

  test('shows loading state initially', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Loading analytics data...')).toBeInTheDocument();
  });

  test('fetches and displays stats data', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/api/stats/');
    });
    
    expect(screen.getByText('Total Events: 48')).toBeInTheDocument();
  });

  test('renders chart sections', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Event Types Distribution')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Daily Event Trends (Last 7 Days)')).toBeInTheDocument();
    expect(screen.getByText('Event Types Breakdown')).toBeInTheDocument();
  });

  test('renders charts when data is available', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });
    
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
  });

  test('renders live feed section', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Recent Events Feed')).toBeInTheDocument();
    });
  });

  test('displays recent events in live feed', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('user_signup')).toBeInTheDocument();
    });
    
    expect(screen.getByText('page_view')).toBeInTheDocument();
    expect(screen.getByText('{"user_id":123}')).toBeInTheDocument();
  });

  test('handles API errors gracefully', async () => {
    const errorMessage = 'Network Error';
    axios.get.mockRejectedValueOnce(new Error(errorMessage));
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(`Failed to fetch analytics data: ${errorMessage}`)).toBeInTheDocument();
    });
  });

  test('handles API errors with response data', async () => {
    axios.get.mockRejectedValueOnce({
      response: { data: { detail: 'API Error' } }
    });
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch analytics data: API Error')).toBeInTheDocument();
    });
  });

  test('refresh button refetches data', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledTimes(1);
    });
    
    const refreshButton = screen.getByText('Refresh Data');
    fireEvent.click(refreshButton);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  test('shows no data message when no events exist', async () => {
    const emptyData = {
      daily_stats: [],
      event_counts: [],
      recent_events: [],
      total_events: 0
    };
    
    axios.get.mockResolvedValueOnce({ data: emptyData });
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Total Events: 0')).toBeInTheDocument();
    });
    
    expect(screen.getByText('No event data available')).toBeInTheDocument();
    expect(screen.getByText('No daily trend data available')).toBeInTheDocument();
    expect(screen.getByText('No event breakdown data available')).toBeInTheDocument();
    expect(screen.getByText('No recent events')).toBeInTheDocument();
  });

  test('formats event timestamps correctly', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      // Check that timestamp is formatted as a locale string
      const timestampElement = screen.getByText((content, element) => {
        return element && element.className === 'event-time' && content.includes('2024');
      });
      expect(timestampElement).toBeInTheDocument();
    });
  });

  test('displays event properties when available', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('{"user_id":123}')).toBeInTheDocument();
    });
  });

  test('handles events without properties', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      // The second event has empty properties, should still render correctly
      expect(screen.getByText('page_view')).toBeInTheDocument();
    });
  });

  test('auto-refresh functionality', async () => {
    jest.useFakeTimers();
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledTimes(1);
    });
    
    // Fast-forward 5 seconds
    jest.advanceTimersByTime(5000);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
    
    jest.useRealTimers();
  });

  test('clears interval on unmount', () => {
    jest.useFakeTimers();
    jest.spyOn(global, 'clearInterval');
    
    const { unmount } = render(<Dashboard />);
    
    unmount();
    
    expect(clearInterval).toHaveBeenCalled();
    
    jest.useRealTimers();
  });

  test('displays correct total events count', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      const totalElement = screen.getByText((content, element) => {
        return element && element.textContent === 'Total Events: 48';
      });
      expect(totalElement).toBeInTheDocument();
    });
  });
});