import { useState, useEffect } from 'react';
import { dataAPI } from '../services/api';

const ProjectLanguage = ({ projectId, isAdmin = false }) => {
  const [language, setLanguage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [fileCount, setFileCount] = useState(0);
  const [canChangeLanguage, setCanChangeLanguage] = useState(true);

  const languageLabels = {
    fr: {
      name: 'Français',
      flag: '🇫🇷',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800'
    },
    en: {
      name: 'English',
      flag: '🇬🇧',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-800'
    },
    ar: {
      name: 'العربية',
      flag: '🇸🇦',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-800'
    }
  };

  useEffect(() => {
    if (projectId) {
      fetchLanguage();
    }
  }, [projectId]);

  const fetchLanguage = async () => {
    try {
      setLoading(true);
      const response = await dataAPI.getProjectLanguage(projectId);
      setLanguage(response.data.language);
      setSelectedLanguage(response.data.language);
      setFileCount(response.data.file_count || 0);
      setCanChangeLanguage(response.data.can_change_language !== false);
      setMessage({ type: '', text: '' });
    } catch (error) {
      console.error('Error fetching language:', error);
      setLanguage('fr'); // Default
      setSelectedLanguage('fr');
      setFileCount(0);
      setCanChangeLanguage(true);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLanguage = async () => {
    if (!selectedLanguage) return;

    try {
      setLoading(true);
      setMessage({ type: '', text: '' });
      await dataAPI.updateProjectLanguage(projectId, selectedLanguage);
      setLanguage(selectedLanguage);
      setEditing(false);
      setMessage({
        type: 'success',
        text: `Langue mise à jour: ${languageLabels[selectedLanguage].name}`
      });

      // Clear message after 3 seconds
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || 'Erreur lors de la mise à jour';
      setMessage({
        type: 'error',
        text: errorMessage
      });
      setEditing(false);

      // Refresh to get updated file count
      await fetchLanguage();
    } finally {
      setLoading(false);
    }
  };

  if (loading && !language) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
        <span>Chargement...</span>
      </div>
    );
  }

  if (!language) return null;

  const currentLang = languageLabels[language] || languageLabels['fr'];

  return (
    <div className="space-y-2">
      {!editing ? (
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${currentLang.bgColor} border ${currentLang.borderColor}`}>
            <span className="text-lg">{currentLang.flag}</span>
            <span className={`text-sm font-medium ${currentLang.textColor}`}>
              {currentLang.name}
            </span>
          </div>

          {isAdmin && canChangeLanguage && (
            <button
              onClick={() => setEditing(true)}
              className="text-sm text-primary hover:text-blue-600 font-medium transition"
            >
              Modifier
            </button>
          )}

          {isAdmin && !canChangeLanguage && (
            <span className="text-xs text-gray-500 italic">
              ({fileCount} fichier{fileCount > 1 ? 's' : ''} - langue verrouillée)
            </span>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-transparent"
              disabled={loading}
            >
              {Object.entries(languageLabels).map(([code, info]) => (
                <option key={code} value={code}>
                  {info.flag} {info.name}
                </option>
              ))}
            </select>

            <button
              onClick={handleUpdateLanguage}
              disabled={loading || selectedLanguage === language}
              className="px-3 py-1.5 bg-primary text-white rounded-lg text-sm hover:bg-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Enregistrement...' : 'Enregistrer'}
            </button>

            <button
              onClick={() => {
                setEditing(false);
                setSelectedLanguage(language);
                setMessage({ type: '', text: '' });
              }}
              disabled={loading}
              className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300 transition"
            >
              Annuler
            </button>
          </div>
        </div>
      )}

      {message.text && (
        <div className={`text-xs p-2 rounded ${
          message.type === 'success'
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        }`}>
          {message.text}
        </div>
      )}
    </div>
  );
};

export default ProjectLanguage;
