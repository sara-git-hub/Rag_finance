import { useState } from 'react';
import { dataAPI } from '../services/api';
import Navbar from '../components/Navbar';
import ProjectLanguage from '../components/ProjectLanguage';
import { useAuth } from '../context/AuthContext';

const Process = () => {
  const [projectId, setProjectId] = useState('1');
  const [fileId, setFileId] = useState('');
  const [chunkSize, setChunkSize] = useState(1000);
  const [overlapSize, setOverlapSize] = useState(200);
  const [doReset, setDoReset] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const { user } = useAuth();

  const handleProcess = async (e) => {
    e.preventDefault();

    if (!projectId) {
      setMessage({ type: 'error', text: 'Veuillez entrer un ID de projet' });
      return;
    }

    setProcessing(true);
    setMessage({ type: '', text: '' });

    try {
      const payload = {
        chunk_size: parseInt(chunkSize),
        overlap_size: parseInt(overlapSize),
        do_reset: doReset ? 1 : 0,
      };

      // Add file_id only if provided
      if (fileId.trim()) {
        payload.file_id = fileId.trim();
      }

      const response = await dataAPI.processData(projectId, payload);

      setMessage({
        type: 'success',
        text: `Traitement réussi! ${response.data.processed_files} fichier(s) traité(s), ${response.data.inserted_chunks} chunk(s) créé(s)`
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.response?.data?.signal || 'Erreur lors du traitement'
      });
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Traitement des Documents</h1>

            <form onSubmit={handleProcess} className="space-y-6">
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

              {/* File ID Input (Optional) */}
              <div>
                <label htmlFor="file-id" className="block text-sm font-medium text-gray-700 mb-2">
                  ID du Fichier <span className="text-gray-500 text-xs">(optionnel)</span>
                </label>
                <input
                  type="text"
                  id="file-id"
                  value={fileId}
                  onChange={(e) => setFileId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Laissez vide pour traiter tous les fichiers"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Si vide, tous les fichiers du projet seront traités
                </p>
              </div>

              {/* Chunk Size Input */}
              <div>
                <label htmlFor="chunk-size" className="block text-sm font-medium text-gray-700 mb-2">
                  Taille des Chunks (caractères)
                </label>
                <input
                  type="number"
                  id="chunk-size"
                  value={chunkSize}
                  onChange={(e) => setChunkSize(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  min="100"
                  max="10000"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Recommandé: 1000-2000 caractères
                </p>
              </div>

              {/* Overlap Size Input */}
              <div>
                <label htmlFor="overlap-size" className="block text-sm font-medium text-gray-700 mb-2">
                  Taille du Chevauchement (caractères)
                </label>
                <input
                  type="number"
                  id="overlap-size"
                  value={overlapSize}
                  onChange={(e) => setOverlapSize(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  min="0"
                  max="1000"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Recommandé: 10-20% de la taille des chunks
                </p>
              </div>

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
                  Réinitialiser les données existantes (supprime les chunks et vecteurs)
                </label>
              </div>

              {doReset && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm text-yellow-800">
                    <strong>Attention:</strong> Cette option supprimera tous les chunks et vecteurs existants du projet avant le traitement.
                  </p>
                </div>
              )}

              {/* Process Button */}
              <button
                type="submit"
                disabled={processing}
                className="w-full bg-primary text-white py-3 px-4 rounded-lg hover:bg-blue-600 transition duration-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processing ? 'Traitement en cours...' : 'Lancer le Traitement'}
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

            {/* Info Box */}
            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-2">À propos du traitement:</h3>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                <li>Découpe les documents en chunks de texte</li>
                <li>Le chevauchement permet de conserver le contexte entre chunks</li>
                <li>Les chunks sont stockés en base de données</li>
                <li>Prérequis pour l'indexation vectorielle</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Process;
