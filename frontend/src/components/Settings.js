import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ANALYTICS_CONFIG from '../config';

const Settings = ({ selectedProject }) => {
  const [projectSettings, setProjectSettings] = useState({
    name: '',
    rate_limit_per_minute: 1000,
    allowed_sources: [],
    is_active: true,
    is_default: false
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);
  const [newSource, setNewSource] = useState('');

  // Load config
  const API_BASE_URL = ANALYTICS_CONFIG.API_BASE_URL;

  const fetchProjectSettings = async () => {
    if (!selectedProject) return;
    
    try {
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/project-settings/?api_key=${selectedProject.api_key}`);
      setProjectSettings(response.data);
    } catch (error) {
      setError('Failed to fetch project settings: ' + (error.response?.data?.detail || error.message));
      console.error('Error fetching project settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveProjectSettings = async () => {
    if (!selectedProject) return;
    
    setSaving(true);
    setMessage('');
    
    try {
      await axios.put(`${API_BASE_URL}/project-settings/`, {
        ...projectSettings,
        api_key: selectedProject.api_key
      });
      setMessage('Settings saved successfully!');
    } catch (error) {
      setMessage('Error saving settings: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
    }
  };

  const addAllowedSource = () => {
    if (newSource.trim() && !projectSettings.allowed_sources.includes(newSource.trim())) {
      setProjectSettings(prev => ({
        ...prev,
        allowed_sources: [...prev.allowed_sources, newSource.trim()]
      }));
      setNewSource('');
    }
  };

  const removeAllowedSource = (sourceToRemove) => {
    setProjectSettings(prev => ({
      ...prev,
      allowed_sources: prev.allowed_sources.filter(source => source !== sourceToRemove)
    }));
  };

  useEffect(() => {
    if (selectedProject) {
      setLoading(true);
      fetchProjectSettings();
    }
  }, [selectedProject]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return <div className="loading">Loading project settings...</div>;
  }

  return (
    <div className="settings">
      <div className="settings-header">
        <h2>⚙️ Project Settings - {selectedProject?.name}</h2>
        <p className="settings-subtitle">Configure settings for this project</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="settings-container">
        {/* Project Information */}
        <div className="settings-section">
          <h3>Project Information</h3>
          <div className="form-group">
            <label htmlFor="projectName">Project Name</label>
            <input
              id="projectName"
              type="text"
              value={projectSettings.name}
              onChange={(e) => setProjectSettings(prev => ({ ...prev, name: e.target.value }))}
              className="form-control"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="projectStatus">
              <input
                id="projectStatus"
                type="checkbox"
                checked={projectSettings.is_active}
                onChange={(e) => setProjectSettings(prev => ({ ...prev, is_active: e.target.checked }))}
              />
              Project Active
            </label>
            <small className="form-help">Inactive projects cannot receive events</small>
          </div>
          
          <div className="form-group">
            <label htmlFor="projectDefault">
              <input
                id="projectDefault"
                type="checkbox"
                checked={projectSettings.is_default}
                onChange={(e) => setProjectSettings(prev => ({ ...prev, is_default: e.target.checked }))}
              />
              Default Project
            </label>
            <small className="form-help">Make this the default project when opening the dashboard</small>
          </div>
        </div>

        {/* Rate Limiting */}
        <div className="settings-section">
          <h3>Rate Limiting</h3>
          <div className="form-group">
            <label htmlFor="rateLimit">Events per Minute</label>
            <input
              id="rateLimit"
              type="number"
              min="1"
              max="10000"
              value={projectSettings.rate_limit_per_minute}
              onChange={(e) => setProjectSettings(prev => ({ 
                ...prev, 
                rate_limit_per_minute: parseInt(e.target.value) || 1000 
              }))}
              className="form-control"
            />
            <small className="form-help">Maximum number of events this project can send per minute</small>
          </div>
        </div>

        {/* Allowed Sources */}
        <div className="settings-section">
          <h3>Allowed Sources</h3>
          <p className="section-description">
            Restrict which sources can send events to this project. Leave empty to allow all sources.
          </p>
          
          <div className="allowed-sources-list">
            {projectSettings.allowed_sources.length > 0 ? (
              projectSettings.allowed_sources.map((source, index) => (
                <div key={index} className="source-item">
                  <span className="source-name">{source}</span>
                  <button
                    type="button"
                    onClick={() => removeAllowedSource(source)}
                    className="remove-source-btn"
                    title="Remove source"
                  >
                    ✕
                  </button>
                </div>
              ))
            ) : (
              <p className="no-sources">No source restrictions - all sources allowed</p>
            )}
          </div>

          <div className="add-source-form">
            <input
              type="text"
              value={newSource}
              onChange={(e) => setNewSource(e.target.value)}
              placeholder="Enter source name (e.g., 'web', 'mobile-app')"
              className="form-control"
              onKeyPress={(e) => e.key === 'Enter' && addAllowedSource()}
            />
            <button
              type="button"
              onClick={addAllowedSource}
              className="add-source-btn"
              disabled={!newSource.trim()}
            >
              Add Source
            </button>
          </div>
          
          <small className="form-help">
            Common sources: web, mobile-app, snake-game, flappy-hedgehog
          </small>
        </div>

        {/* API Keys Display */}
        <div className="settings-section">
          <h3>API Keys</h3>
          <div className="api-keys-info">
            <div className="api-key-item">
              <label>Public API Key (for client-side events)</label>
              <div className="api-key-display">
                <code>{selectedProject?.api_key}</code>
                <button
                  onClick={() => navigator.clipboard.writeText(selectedProject?.api_key)}
                  className="copy-btn"
                  title="Copy to clipboard"
                >
                  📋
                </button>
              </div>
            </div>
            <small className="form-help">
              This key is safe to use in frontend applications. Secret key management would require server-side implementation.
            </small>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="settings-actions">
        <button
          onClick={saveProjectSettings}
          disabled={saving}
          className="save-btn"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
        
        <button
          onClick={fetchProjectSettings}
          className="refresh-btn"
        >
          Refresh
        </button>
      </div>

      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default Settings;