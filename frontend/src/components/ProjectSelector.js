import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProjectSelector = ({ selectedProject, onProjectChange, apiBaseUrl }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProjects = async () => {
    try {
      setError(null);
      const response = await axios.get(`${apiBaseUrl}/projects/`);
      setProjects(response.data);
      
      // Auto-select default project if no project is selected
      if (!selectedProject && response.data.length > 0) {
        const defaultProject = response.data.find(p => p.is_default);
        if (defaultProject && onProjectChange) {
          onProjectChange(defaultProject);
        }
      }
    } catch (error) {
      setError('Failed to fetch projects: ' + (error.response?.data?.detail || error.message));
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleProjectChange = (event) => {
    const projectId = parseInt(event.target.value);
    const project = projects.find(p => p.id === projectId);
    if (project && onProjectChange) {
      onProjectChange(project);
    }
  };

  const getProjectIcon = (slug) => {
    const iconMap = {
      'default': '📊',
      'snake-game': '🐍',
      'flappy-hedgehog': '🦔'
    };
    return iconMap[slug] || '🔧';
  };

  if (loading) {
    return <div className="project-selector loading">Loading projects...</div>;
  }

  if (error) {
    return (
      <div className="project-selector error">
        <span className="error-text">{error}</span>
        <button onClick={fetchProjects} className="retry-btn">Retry</button>
      </div>
    );
  }

  return (
    <div className="project-selector">
      <label htmlFor="project-select" className="project-label">
        📁 Project:
      </label>
      <select 
        id="project-select"
        value={selectedProject?.id || ''} 
        onChange={handleProjectChange}
        className="project-select"
      >
        {!selectedProject && (
          <option value="">Select a project...</option>
        )}
        {projects.map(project => (
          <option key={project.id} value={project.id}>
            {getProjectIcon(project.slug)} {project.name} {project.is_default ? '⭐ (Default)' : ''}
          </option>
        ))}
      </select>
      
      {selectedProject && (
        <div className="selected-project-info">
          <span className="project-name">
            {getProjectIcon(selectedProject.slug)} {selectedProject.name}
          </span>
          <span className="api-key-preview">
            {selectedProject.api_key.substring(0, 20)}...
          </span>
        </div>
      )}
    </div>
  );
};

export default ProjectSelector;