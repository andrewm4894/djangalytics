import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EventCapture from './EventCapture';

// Mock axios
jest.mock('axios', () => ({
  post: jest.fn()
}));

import axios from 'axios';

describe('EventCapture Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders event capture form', () => {
    render(<EventCapture />);
    
    expect(screen.getByText('Capture Event')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter event name...')).toBeInTheDocument();
    expect(screen.getByText('Capture Event')).toBeInTheDocument();
  });

  test('renders quick event buttons', () => {
    render(<EventCapture />);
    
    expect(screen.getByText('Quick Events:')).toBeInTheDocument();
    expect(screen.getByText('user_signup')).toBeInTheDocument();
    expect(screen.getByText('user_login')).toBeInTheDocument();
    expect(screen.getByText('page_view')).toBeInTheDocument();
    expect(screen.getByText('button_click')).toBeInTheDocument();
    expect(screen.getByText('form_submit')).toBeInTheDocument();
  });

  test('enables submit button only when event name is entered', () => {
    render(<EventCapture />);
    
    const input = screen.getByPlaceholderText('Enter event name...');
    const submitButton = screen.getByRole('button', { name: /capture event/i });
    
    // Initially disabled
    expect(submitButton).toBeDisabled();
    
    // Enable after typing
    fireEvent.change(input, { target: { value: 'test_event' } });
    expect(submitButton).not.toBeDisabled();
    
    // Disable again if cleared
    fireEvent.change(input, { target: { value: '' } });
    expect(submitButton).toBeDisabled();
  });

  test('submits form with event name', async () => {
    axios.post.mockResolvedValueOnce({
      data: {
        id: 1,
        event_name: 'test_event',
        timestamp: '2024-01-01T12:00:00Z',
        message: 'Event captured successfully'
      }
    });

    render(<EventCapture />);
    
    const input = screen.getByPlaceholderText('Enter event name...');
    const submitButton = screen.getByRole('button', { name: /capture event/i });
    
    fireEvent.change(input, { target: { value: 'test_event' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/capture_event/',
        expect.objectContaining({
          event_name: 'test_event',
          timestamp: expect.any(String)
        })
      );
    });
    
    expect(screen.getByText('Event "test_event" captured successfully!')).toBeInTheDocument();
    expect(input.value).toBe(''); // Form should be cleared
  });

  test('handles API error gracefully', async () => {
    axios.post.mockRejectedValueOnce({
      response: { data: { detail: 'API Error' } }
    });

    render(<EventCapture />);
    
    const input = screen.getByPlaceholderText('Enter event name...');
    const submitButton = screen.getByRole('button', { name: /capture event/i });
    
    fireEvent.change(input, { target: { value: 'test_event' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Error capturing event: API Error')).toBeInTheDocument();
    });
  });

  test('quick event buttons work', async () => {
    axios.post.mockResolvedValueOnce({
      data: { message: 'Event captured successfully' }
    });

    render(<EventCapture />);
    
    const signupButton = screen.getByText('user_signup');
    fireEvent.click(signupButton);
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/capture_event/',
        expect.objectContaining({
          event_name: 'user_signup',
          timestamp: expect.any(String)
        })
      );
    });
    
    expect(screen.getByText('Event "user_signup" captured!')).toBeInTheDocument();
  });

  test('shows loading state during submission', async () => {
    // Create a promise that we can control
    let resolvePromise;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    
    axios.post.mockReturnValueOnce(promise);

    render(<EventCapture />);
    
    const input = screen.getByPlaceholderText('Enter event name...');
    const submitButton = screen.getByRole('button', { name: /capture event/i });
    
    fireEvent.change(input, { target: { value: 'test_event' } });
    fireEvent.click(submitButton);
    
    // Check loading state
    expect(screen.getByText('Capturing...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
    
    // Resolve the promise
    resolvePromise({ data: { message: 'Success' } });
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /capture event/i })).not.toBeDisabled();
    });
  });

  test('disables buttons during loading', async () => {
    let resolvePromise;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    
    axios.post.mockReturnValueOnce(promise);

    render(<EventCapture />);
    
    const signupButton = screen.getByText('user_signup');
    fireEvent.click(signupButton);
    
    // All quick event buttons should be disabled during loading
    const quickEventButtons = screen.getAllByRole('button').filter(
      button => button.classList.contains('quick-event-btn') || button.textContent.includes('user_')
    );
    
    quickEventButtons.forEach(button => {
      if (button.textContent.includes('user_')) {
        expect(button).toBeDisabled();
      }
    });
    
    // Resolve the promise
    resolvePromise({ data: { message: 'Success' } });
    
    await waitFor(() => {
      expect(signupButton).not.toBeDisabled();
    });
  });

  test('prevents form submission when loading', async () => {
    let resolvePromise;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    
    axios.post.mockReturnValueOnce(promise);

    render(<EventCapture />);
    
    const input = screen.getByPlaceholderText('Enter event name...');
    const form = input.closest('form');
    
    fireEvent.change(input, { target: { value: 'test_event' } });
    fireEvent.submit(form);
    
    // Try to submit again while loading
    fireEvent.submit(form);
    
    // Should only be called once
    expect(axios.post).toHaveBeenCalledTimes(1);
    
    resolvePromise({ data: { message: 'Success' } });
  });

  test('handles network errors', async () => {
    axios.post.mockRejectedValueOnce(new Error('Network Error'));

    render(<EventCapture />);
    
    const input = screen.getByPlaceholderText('Enter event name...');
    const submitButton = screen.getByRole('button', { name: /capture event/i });
    
    fireEvent.change(input, { target: { value: 'test_event' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Error capturing event: Network Error')).toBeInTheDocument();
    });
  });
});