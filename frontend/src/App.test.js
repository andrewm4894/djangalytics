import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock the child components to avoid complex dependencies
jest.mock('./components/Dashboard', () => {
  return function MockDashboard() {
    return <div data-testid="dashboard">Dashboard Component</div>;
  };
});

jest.mock('./components/EventCapture', () => {
  return function MockEventCapture() {
    return <div data-testid="event-capture">EventCapture Component</div>;
  };
});

// Mock axios to prevent network calls
jest.mock('axios');

describe('App Component', () => {
  test('renders main application header', () => {
    render(<App />);
    
    expect(screen.getByText('Djangalytics - Event Analytics Dashboard')).toBeInTheDocument();
  });

  test('renders EventCapture component', () => {
    render(<App />);
    
    expect(screen.getByTestId('event-capture')).toBeInTheDocument();
  });

  test('renders Dashboard component', () => {
    render(<App />);
    
    expect(screen.getByTestId('dashboard')).toBeInTheDocument();
  });

  test('has correct structure with header and main sections', () => {
    render(<App />);
    
    const appDiv = document.querySelector('.App');
    expect(appDiv).toBeInTheDocument();
    
    const header = document.querySelector('.App-header');
    expect(header).toBeInTheDocument();
    
    const main = document.querySelector('.App-main');
    expect(main).toBeInTheDocument();
  });

  test('components are rendered in correct order', () => {
    render(<App />);
    
    const main = document.querySelector('.App-main');
    const children = Array.from(main.children);
    
    expect(children[0]).toHaveAttribute('data-testid', 'event-capture');
    expect(children[1]).toHaveAttribute('data-testid', 'dashboard');
  });
});
