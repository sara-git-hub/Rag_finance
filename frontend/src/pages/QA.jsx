import { useState, useRef, useEffect } from 'react';
import { useConversation } from '../hooks/useConversation';
import Navbar from '../components/Navbar';
import ProjectLanguage from '../components/ProjectLanguage';
import { useAuth } from '../context/AuthContext';

const QA = () => {
  const [projectId, setProjectId] = useState('4');
  const [question, setQuestion] = useState('');
  const [limit] = useState(5);
  const [showSidebar, setShowSidebar] = useState(true);
  const messagesEndRef = useRef(null);
  const { user } = useAuth();

  const {
    conversations,
    currentConversation,
    messages,
    loading,
    error,
    createConversation,
    loadConversation,
    askQuestion,
    deleteConversation,
    hasMessages,
  } = useConversation(projectId);

  // Auto-scroll vers le bas quand de nouveaux messages arrivent
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleAsk = async (e) => {
    e.preventDefault();

    if (!question.trim()) return;

    const result = await askQuestion(question, limit);

    if (result) {
      setQuestion(''); // Clear input après succès
    }
  };

  const handleNewConversation = async () => {
    await createConversation();
  };

  const handleSelectConversation = async (convId) => {
    await loadConversation(convId);
  };

  const handleDeleteConversation = async (convId, e) => {
    e.stopPropagation(); // Empêcher la sélection lors de la suppression

    if (window.confirm('Voulez-vous vraiment supprimer cette conversation ?')) {
      await deleteConversation(convId);
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />

      <div className="container mx-auto px-4 py-6">
        <div className="flex gap-4 max-w-7xl mx-auto" style={{ height: 'calc(100vh - 10rem)' }}>

          {/* SIDEBAR - Liste des conversations */}
          {showSidebar && (
            <div className="w-80 bg-white rounded-lg shadow-xl flex flex-col overflow-hidden">
              {/* Header Sidebar */}
              <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-primary to-blue-600">
                <div className="flex justify-between items-center mb-3">
                  <h2 className="font-bold text-white">Conversations</h2>
                  <button
                    onClick={handleNewConversation}
                    className="bg-white text-primary px-3 py-1.5 rounded-lg text-sm font-semibold hover:bg-gray-100 transition"
                  >
                    + Nouveau
                  </button>
                </div>

                {/* Sélecteur de Projet */}
                <div className="space-y-2">
                  <label htmlFor="project-id-qa" className="block text-xs font-medium text-blue-100 mb-1">
                    ID du Projet
                  </label>
                  <input
                    type="number"
                    id="project-id-qa"
                    value={projectId}
                    onChange={(e) => setProjectId(e.target.value)}
                    className="w-full px-3 py-1.5 border border-blue-300 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-sm"
                    placeholder="Entrez l'ID du projet"
                    min="1"
                  />

                  {/* Project Language Display */}
                  {projectId && (
                    <div className="pt-1">
                      <label className="block text-xs font-medium text-blue-100 mb-1">
                        Langue
                      </label>
                      <ProjectLanguage
                        projectId={projectId}
                        isAdmin={user?.role === 'admin'}
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Liste des conversations */}
              <div className="flex-1 overflow-y-auto p-3 space-y-2">
                {conversations.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-sm text-gray-500">Aucune conversation</p>
                    <p className="text-xs text-gray-400 mt-1">Créez-en une pour commencer</p>
                  </div>
                ) : (
                  conversations.map((conv) => (
                    <div
                      key={conv.conversation_id}
                      onClick={() => handleSelectConversation(conv.conversation_id)}
                      className={`group relative p-3 rounded-lg cursor-pointer transition ${
                        currentConversation?.conversation_id === conv.conversation_id
                          ? 'bg-primary text-white shadow-md'
                          : 'bg-gray-50 hover:bg-gray-100 text-gray-800'
                      }`}
                    >
                      <p className="text-sm font-medium truncate pr-6">{conv.title}</p>
                      <p className={`text-xs mt-1 ${
                        currentConversation?.conversation_id === conv.conversation_id
                          ? 'text-blue-100'
                          : 'text-gray-500'
                      }`}>
                        {formatDate(conv.created_at)}
                      </p>

                      {/* Bouton supprimer */}
                      <button
                        onClick={(e) => handleDeleteConversation(conv.conversation_id, e)}
                        className={`absolute top-2 right-2 p-1.5 rounded opacity-0 group-hover:opacity-100 transition ${
                          currentConversation?.conversation_id === conv.conversation_id
                            ? 'hover:bg-blue-600'
                            : 'hover:bg-red-100'
                        }`}
                        title="Supprimer"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* MAIN CHAT AREA */}
          <div className="flex-1 bg-white rounded-lg shadow-xl flex flex-col overflow-hidden">

            {/* Header */}
            <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-primary to-blue-600">
              <div className="flex justify-between items-center">
                <div>
                  <h1 className="text-xl font-bold text-white">
                    {currentConversation?.title || 'Questions & Réponses (RAG)'}
                  </h1>
                  <p className="text-xs text-blue-100 mt-1">
                    Assistant RAG basé sur vos documents
                  </p>
                </div>
                <button
                  onClick={() => setShowSidebar(!showSidebar)}
                  className="text-white hover:bg-blue-600 p-2 rounded-lg transition"
                  title={showSidebar ? 'Masquer sidebar' : 'Afficher sidebar'}
                >
                  {showSidebar ? (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                    </svg>
                  ) : (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
              {!hasMessages ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="bg-white rounded-full p-6 shadow-lg mb-4">
                    <svg className="w-16 h-16 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  <p className="text-xl font-semibold text-gray-700 mb-2">Commencez une conversation</p>
                  <p className="text-sm text-gray-500 max-w-md">
                    Posez vos questions sur vos documents et obtenez des réponses précises basées sur le contenu indexé.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg, index) => (
                    <div
                      key={index}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                          msg.role === 'user'
                            ? 'bg-primary text-white'
                            : 'bg-white text-gray-800 shadow-md border border-gray-100'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                        <p className={`text-xs mt-2 ${
                          msg.role === 'user' ? 'text-blue-200' : 'text-gray-400'
                        }`}>
                          {formatTime(msg.created_at)}
                        </p>
                      </div>
                    </div>
                  ))}

                  {/* Loading indicator */}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-white rounded-2xl px-4 py-3 shadow-md border border-gray-100">
                        <div className="flex items-center gap-2">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                          </div>
                          <span className="text-sm text-gray-600">Génération de la réponse...</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-200 bg-white">
              {error && (
                <div className="mb-3 p-3 bg-red-50 text-red-800 rounded-lg text-sm border border-red-200">
                  {error}
                </div>
              )}

              <form onSubmit={handleAsk} className="flex gap-3">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Posez votre question..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !question.trim()}
                  className="bg-primary text-white px-6 py-3 rounded-xl hover:bg-blue-600 transition duration-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loading ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                      Envoyer
                    </>
                  )}
                </button>
              </form>

              <p className="text-xs text-gray-500 mt-2 text-center">
                L'assistant se base sur vos documents indexés pour répondre
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QA;
