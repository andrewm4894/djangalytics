import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import ProjectSelector from './components/ProjectSelector';
import ANALYTICS_CONFIG from './config';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedProject, setSelectedProject] = useState(null);

  // Initialize with default project
  useEffect(() => {
    setSelectedProject({
      id: 1,
      name: 'Default Dashboard',
      slug: 'default',
      api_key: ANALYTICS_CONFIG.API_KEY
    });
  }, []);

  const handleProjectChange = (project) => {
    setSelectedProject(project);
  };

  const renderCurrentView = () => {
    if (!selectedProject) {
      return <div className="loading">Please select a project...</div>;
    }

    switch (currentView) {
      case 'dashboard':
        return <Dashboard selectedProject={selectedProject} />;
      case 'settings':
        return <Settings selectedProject={selectedProject} />;
      default:
        return <Dashboard selectedProject={selectedProject} />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-top">
          <h1>Djangalytics - Event Analytics Dashboard</h1>
          <ProjectSelector 
            selectedProject={selectedProject}
            onProjectChange={handleProjectChange}
            apiBaseUrl={ANALYTICS_CONFIG.API_BASE_URL}
          />
        </div>
        <nav className="app-nav">
          <button 
            className={`nav-btn ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('dashboard')}
          >
            📊 Dashboard
          </button>
          <button 
            className={`nav-btn ${currentView === 'settings' ? 'active' : ''}`}
            onClick={() => setCurrentView('settings')}
          >
            ⚙️ Settings
          </button>
        </nav>
      </header>
      <main className="App-main">
        {renderCurrentView()}
      </main>
    </div>
  );
}

export default App;
