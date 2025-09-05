import React, { useState } from 'react';
import axios from 'axios';

const EventCapture = () => {
  const [eventName, setEventName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!eventName.trim()) return;

    setIsLoading(true);
    setMessage('');

    try {
      await axios.post('http://localhost:8000/api/capture_event/', {
        event_name: eventName,
        timestamp: new Date().toISOString()
      });
      
      setMessage(`Event "${eventName}" captured successfully!`);
      setEventName('');
    } catch (error) {
      setMessage('Error capturing event: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsLoading(false);
    }
  };

  const quickEvents = [
    'user_signup',
    'user_login',
    'page_view',
    'button_click',
    'form_submit'
  ];

  const handleQuickEvent = async (event) => {
    setIsLoading(true);
    try {
      await axios.post('http://localhost:8000/api/capture_event/', {
        event_name: event,
        timestamp: new Date().toISOString()
      });
      setMessage(`Event "${event}" captured!`);
    } catch (error) {
      setMessage('Error: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="event-capture">
      <h2>Capture Event</h2>
      <form onSubmit={handleSubmit} className="capture-form">
        <input
          type="text"
          value={eventName}
          onChange={(e) => setEventName(e.target.value)}
          placeholder="Enter event name..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !eventName.trim()}>
          {isLoading ? 'Capturing...' : 'Capture Event'}
        </button>
      </form>

      <div className="quick-events">
        <h3>Quick Events:</h3>
        {quickEvents.map(event => (
          <button 
            key={event} 
            onClick={() => handleQuickEvent(event)}
            disabled={isLoading}
            className="quick-event-btn"
          >
            {event}
          </button>
        ))}
      </div>

      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default EventCapture;