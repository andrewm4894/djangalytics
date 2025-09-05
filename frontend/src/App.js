import React from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import EventCapture from './components/EventCapture';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Djangalytics - Event Analytics Dashboard</h1>
      </header>
      <main className="App-main">
        <EventCapture />
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
