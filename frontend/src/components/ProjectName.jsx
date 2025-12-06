import { useState, useEffect } from 'react';
import { dataAPI } from '../services/api';

const ProjectName = ({ projectId }) => {
  const [projectName, setProjectName] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (projectId) {
      fetchProjectName();
    }
  }, [projectId]);

  const fetchProjectName = async () => {
    try {
      setLoading(true);
      const response = await dataAPI.getProjectLanguage(projectId);
      setProjectName(response.data.project_name);
    } catch (error) {
      console.error('Error fetching project name:', error);
      setProjectName(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
        <span>Chargement...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-50 border border-gray-200">
      <span className="text-sm font-medium text-gray-700">
        {projectName || '(Sans nom)'}
      </span>
    </div>
  );
};

export default ProjectName;
