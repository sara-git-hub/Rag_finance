import { useState } from 'react';
import { nlpAPI } from '../services/api';
import Navbar from '../components/Navbar';
import ProjectLanguage from '../components/ProjectLanguage';
import { useAuth } from '../context/AuthContext';

const Search = () => {
  const [projectId, setProjectId] = useState('1');
  const [searchText, setSearchText] = useState('');
  const [limit, setLimit] = useState(5);
  const [searching, setSearching] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [results, setResults] = useState([]);
  const { user } = useAuth();

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!projectId) {
      setMessage({ type: 'error', text: 'Veuillez entrer un ID de projet' });
      return;
    }

    if (!searchText.trim()) {
      setMessage({ type: 'error', text: 'Veuillez entrer un texte de recherche' });
      return;
    }

    setSearching(true);
    setMessage({ type: '', text: '' });
    setResults([]);

    try {
      const response = await nlpAPI.search(projectId, {
        text: searchText,
        limit: parseInt(limit),
      });

      setResults(response.data.results || []);
      setMessage({
        type: 'success',
        text: `${response.data.results?.length || 0} résultat(s) trouvé(s)`
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.response?.data?.signal || 'Erreur lors de la recherche'
      });
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Search Form Card */}
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Recherche Vectorielle</h1>

            <form onSubmit={handleSearch} className="space-y-6">
              {/* Project ID Input */}
              <div>
                <label htmlFor="project-id" className="block text-sm font-medium text-gray-700 mb-2">
                  ID du Projet *
                </label>
                <input
                  type="number"
                  id="project-id"
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Entrez l'ID du projet"
                  min="1"
                  required
                />
              </div>

              {/* Project Language Display */}
              {projectId && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Langue du Projet
                  </label>
                  <ProjectLanguage
                    projectId={projectId}
                    isAdmin={user?.role === 'admin'}
                  />
                </div>
              )}

              {/* Search Text Input */}
              <div>
                <label htmlFor="search-text" className="block text-sm font-medium text-gray-700 mb-2">
                  Recherche *
                </label>
                <textarea
                  id="search-text"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  rows="4"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                  placeholder="Entrez votre requête de recherche..."
                  required
                />
              </div>

              {/* Limit Input */}
              <div>
                <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre de résultats
                </label>
                <input
                  type="number"
                  id="limit"
                  value={limit}
                  onChange={(e) => setLimit(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  min="1"
                  max="20"
                />
              </div>

              {/* Search Button */}
              <button
                type="submit"
                disabled={searching}
                className="w-full bg-primary text-white py-3 px-4 rounded-lg hover:bg-blue-600 transition duration-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {searching ? 'Recherche en cours...' : 'Rechercher'}
              </button>
            </form>

            {/* Message Display */}
            {message.text && (
              <div className={`mt-6 p-4 rounded-lg ${
                message.type === 'success'
                  ? 'bg-green-100 text-green-800 border border-green-200'
                  : 'bg-red-100 text-red-800 border border-red-200'
              }`}>
                <p className="font-medium">{message.text}</p>
              </div>
            )}
          </div>

          {/* Results Card */}
          {results.length > 0 && (
            <div className="bg-white rounded-lg shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Résultats de la recherche</h2>

              <div className="space-y-4">
                {results.map((result, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition"
                  >
                    {/* Score and Metadata */}
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center gap-3">
                        <span className="bg-primary text-white px-3 py-1 rounded-full text-sm font-semibold">
                          #{index + 1}
                        </span>
                        {result.score !== undefined && (
                          <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold border border-green-200">
                            Score: {result.score.toFixed(4)}
                          </span>
                        )}
                      </div>
                      {result.id && (
                        <span className="text-xs text-gray-500">ID: {result.id}</span>
                      )}
                    </div>

                    {/* Content */}
                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                        {result.payload?.text || result.text || 'Pas de texte disponible'}
                      </p>
                    </div>

                    {/* Metadata Display */}
                    {result.payload && Object.keys(result.payload).length > 1 && (
                      <div className="border-t border-gray-200 pt-4">
                        <h4 className="text-xs font-semibold text-gray-600 mb-2 uppercase">Métadonnées</h4>
                        <div className="grid grid-cols-2 gap-2">
                          {Object.entries(result.payload).map(([key, value]) => {
                            if (key === 'text') return null;
                            return (
                              <div key={key} className="text-xs">
                                <span className="text-gray-500">{key}:</span>{' '}
                                <span className="text-gray-700 font-medium">
                                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No Results Message */}
          {!searching && results.length === 0 && message.type === 'success' && (
            <div className="bg-white rounded-lg shadow-xl p-8 text-center">
              <p className="text-gray-500 text-lg">Aucun résultat trouvé pour votre recherche</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Search;
