import { useState } from 'react';
import { nlpAPI } from '../services/api';
import Navbar from '../components/Navbar';

const QA = () => {
  const [projectId, setProjectId] = useState('1');
  const [question, setQuestion] = useState('');
  const [limit, setLimit] = useState(5);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [answer, setAnswer] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();

    if (!projectId) {
      setMessage({ type: 'error', text: 'Veuillez entrer un ID de projet' });
      return;
    }

    if (!question.trim()) {
      setMessage({ type: 'error', text: 'Veuillez entrer une question' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });
    setAnswer(null);

    try {
      const response = await nlpAPI.answer(projectId, {
        text: question,
        limit: parseInt(limit),
      });

      setAnswer(response.data);
      setMessage({
        type: 'success',
        text: 'Réponse générée avec succès'
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.response?.data?.signal || 'Erreur lors de la génération de la réponse'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Question Form Card */}
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Questions & Réponses (RAG)</h1>

            <form onSubmit={handleAsk} className="space-y-6">
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

              {/* Question Input */}
              <div>
                <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
                  Question *
                </label>
                <textarea
                  id="question"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  rows="4"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                  placeholder="Posez votre question ici..."
                  required
                />
              </div>

              {/* Limit Input */}
              <div>
                <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre de documents de contexte
                </label>
                <input
                  type="number"
                  id="limit"
                  value={limit}
                  onChange={(e) => setLimit(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  min="1"
                  max="10"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Nombre de chunks à utiliser comme contexte pour générer la réponse
                </p>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary text-white py-3 px-4 rounded-lg hover:bg-blue-600 transition duration-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Génération de la réponse...' : 'Poser la Question'}
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
              <h3 className="font-semibold text-gray-800 mb-2">À propos du RAG:</h3>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                <li>Recherche vectorielle pour trouver les documents pertinents</li>
                <li>Génération de réponses basée sur le contexte trouvé</li>
                <li>Utilise un LLM pour formuler des réponses naturelles</li>
                <li>Les réponses sont basées uniquement sur vos documents</li>
              </ul>
            </div>
          </div>

          {/* Answer Card */}
          {answer && (
            <div className="bg-white rounded-lg shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Réponse</h2>

              {/* Main Answer */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6 border border-blue-200">
                <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap">
                  {answer.answer}
                </p>
              </div>

              {/* Toggle Buttons */}
              <div className="flex gap-4 mb-4">
                <button
                  onClick={() => setShowPrompt(!showPrompt)}
                  className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition duration-200 font-semibold"
                >
                  {showPrompt ? 'Masquer' : 'Afficher'} le Prompt
                </button>
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition duration-200 font-semibold"
                >
                  {showHistory ? 'Masquer' : 'Afficher'} l'Historique
                </button>
              </div>

              {/* Full Prompt */}
              {showPrompt && answer.full_prompt && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Prompt Complet</h3>
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 max-h-96 overflow-y-auto">
                    <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                      {answer.full_prompt}
                    </pre>
                  </div>
                </div>
              )}

              {/* Chat History */}
              {showHistory && answer.chat_history && answer.chat_history.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">
                    Historique des Messages ({answer.chat_history.length})
                  </h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {answer.chat_history.map((msg, index) => (
                      <div
                        key={index}
                        className={`rounded-lg p-4 ${
                          msg.role === 'user'
                            ? 'bg-blue-50 border border-blue-200'
                            : 'bg-green-50 border border-green-200'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${
                            msg.role === 'user'
                              ? 'bg-blue-200 text-blue-800'
                              : 'bg-green-200 text-green-800'
                          }`}>
                            {msg.role === 'user' ? 'Utilisateur' : 'Assistant'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    ))}
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

export default QA;
