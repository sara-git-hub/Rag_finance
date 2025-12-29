import { useState } from 'react';
import { dataAPI } from '../services/api';
import Navbar from '../components/Navbar';
import ProjectLanguage from '../components/ProjectLanguage';
import { useAuth } from '../context/AuthContext';

const Upload = () => {
  const [projectId, setProjectId] = useState('1');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const { user } = useAuth();

  console.log('Upload - User from context:', user);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setMessage({ type: '', text: '' });
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      setMessage({ type: 'error', text: 'Veuillez sélectionner un fichier' });
      return;
    }

    if (!projectId) {
      setMessage({ type: 'error', text: 'Veuillez entrer un ID de projet' });
      return;
    }

    setUploading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await dataAPI.uploadFile(projectId, selectedFile);
      setMessage({
        type: 'success',
        text: `Fichier uploadé avec succès! ID: ${response.data.file_id}`
      });
      setSelectedFile(null);
      document.getElementById('file-input').value = '';
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.response?.data?.signal || 'Erreur lors de l\'upload'
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Upload de Fichiers</h1>

            <form onSubmit={handleUpload} className="space-y-6">
              {/* Project ID Input */}
              <div>
                <label htmlFor="project-id" className="block text-sm font-medium text-gray-700 mb-2">
                  ID du Projet
                </label>
                <input
                  type="number"
                  id="project-id"
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Entrez l'ID du projet"
                  min="1"
                />
              </div>

              {/* Project Language Display/Edit */}
              {projectId && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Langue du Projet
                  </label>
                  <ProjectLanguage
                    projectId={projectId}
                    isAdmin={user?.role === 'admin'}
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    La langue détermine les prompts utilisés par le système RAG
                  </p>
                </div>
              )}

              {/* File Input */}
              <div>
                <label htmlFor="file-input" className="block text-sm font-medium text-gray-700 mb-2">
                  Sélectionner un fichier
                </label>
                <input
                  type="file"
                  id="file-input"
                  onChange={handleFileChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-blue-600"
                  accept=".pdf,.txt"
                />
                {selectedFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    Fichier sélectionné: <span className="font-medium">{selectedFile.name}</span> ({(selectedFile.size / 1024).toFixed(2)} KB)
                  </p>
                )}
              </div>

              {/* Upload Button */}
              <button
                type="submit"
                disabled={uploading}
                className="w-full bg-primary text-white py-3 px-4 rounded-lg hover:bg-blue-600 transition duration-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? 'Upload en cours...' : 'Upload Fichier'}
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
              <h3 className="font-semibold text-gray-800 mb-2">Formats supportés:</h3>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                <li>PDF (.pdf)</li>
                <li>Texte (.txt)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;
