import { useState } from 'react';
import { nlpAPI } from '../services/api';
import Navbar from '../components/Navbar';
import ProjectLanguage from '../components/ProjectLanguage';
import { useAuth } from '../context/AuthContext';

const IndexPage = () => {
  const [projectId, setProjectId] = useState('1');
  const [doReset, setDoReset] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [collectionInfo, setCollectionInfo] = useState(null);
  const { user } = useAuth();

  const handleIndex = async (e) => {
    e.preventDefault();

    if (!projectId) {
      setMessage({ type: 'error', text: 'Veuillez entrer un ID de projet' });
      return;
    }

    setIndexing(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await nlpAPI.pushToIndex(projectId, {
        do_reset: doReset ? 1 : 0,
      });

      setMessage({
        type: 'success',
        text: `Indexation réussie! ${response.data.inserted_items_count} vecteur(s) indexé(s)`
      });

      // Refresh collection info after indexing
      setTimeout(() => fetchCollectionInfo(), 1000);
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.response?.data?.signal || 'Erreur lors de l\'indexation'
      });
    } finally {
      setIndexing(false);
    }
  };

  const fetchCollectionInfo = async () => {
    if (!projectId) {
      setMessage({ type: 'error', text: 'Veuillez entrer un ID de projet' });
      return;
    }

    setLoadingInfo(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await nlpAPI.getIndexInfo(projectId);
      setCollectionInfo(response.data.collection_info);
      setMessage({ type: 'success', text: 'Informations récupérées avec succès' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.response?.data?.signal || 'Erreur lors de la récupération des informations'
      });
      setCollectionInfo(null);
    } finally {
      setLoadingInfo(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Indexation Card */}
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Indexation Vectorielle</h1>

            <form onSubmit={handleIndex} className="space-y-6">
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

              {/* Reset Checkbox */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="do-reset"
                  checked={doReset}
                  onChange={(e) => setDoReset(e.target.checked)}
                  className="w-4 h-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <label htmlFor="do-reset" className="ml-2 text-sm text-gray-700">
                  Réinitialiser la collection vectorielle (supprime tous les vecteurs)
                </label>
              </div>

              {doReset && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm text-yellow-800">
                    <strong>Attention:</strong> Cette option supprimera tous les vecteurs existants de la collection avant l'indexation.
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={indexing}
                  className="flex-1 bg-primary text-white py-3 px-4 rounded-lg hover:bg-blue-600 transition duration-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {indexing ? 'Indexation en cours...' : 'Lancer l\'Indexation'}
                </button>

                <button
                  type="button"
                  onClick={fetchCollectionInfo}
                  disabled={loadingInfo}
                  className="flex-1 bg-secondary text-white py-3 px-4 rounded-lg hover:bg-green-600 transition duration-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loadingInfo ? 'Chargement...' : 'Voir les Infos'}
                </button>
              </div>
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

            {/* Info Box */}
            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-2">À propos de l'indexation:</h3>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                <li>Convertit les chunks de texte en vecteurs (embeddings)</li>
                <li>Stocke les vecteurs dans Qdrant pour la recherche sémantique</li>
                <li>Prérequis: les documents doivent être traités d'abord</li>
                <li>L'indexation peut prendre du temps pour de gros volumes</li>
              </ul>
            </div>
          </div>

          {/* Collection Info Card */}
          {collectionInfo && (
            <div className="bg-white rounded-lg shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Informations de la Collection</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-600 mb-1">Nom de la Collection</h3>
                  <p className="text-xl font-bold text-gray-800">{collectionInfo.collection_name || 'N/A'}</p>
                </div>

                <div className="bg-green-50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-600 mb-1">Nombre de Vecteurs</h3>
                  <p className="text-xl font-bold text-gray-800">
                    {(collectionInfo.vectors_count !== undefined && collectionInfo.vectors_count !== null && typeof collectionInfo.vectors_count === 'number')
                      ? collectionInfo.vectors_count.toLocaleString()
                      : (collectionInfo.vectors_count || 'N/A')}
                  </p>
                </div>

                <div className="bg-purple-50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-600 mb-1">Dimension des Vecteurs</h3>
                  <p className="text-xl font-bold text-gray-800">{collectionInfo.vector_size || 'N/A'}</p>
                </div>

                <div className="bg-yellow-50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-600 mb-1">Statut</h3>
                  <p className="text-xl font-bold text-gray-800">
                    {collectionInfo.status || 'Actif'}
                  </p>
                </div>
              </div>

              {collectionInfo.indexed_vectors_count !== undefined && collectionInfo.indexed_vectors_count !== null && (
                <div className="mt-6 bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-600">Vecteurs Indexés</span>
                    <span className="text-lg font-bold text-gray-800">
                      {typeof collectionInfo.indexed_vectors_count === 'number'
                        ? collectionInfo.indexed_vectors_count.toLocaleString()
                        : collectionInfo.indexed_vectors_count}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IndexPage;
