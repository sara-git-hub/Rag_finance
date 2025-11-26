import { useState, useEffect } from 'react';
import { conversationAPI, nlpAPI } from '../services/api';

/**
 * Hook personnalisé pour gérer les conversations RAG
 *
 * @param {number|string} projectId - ID du projet
 * @returns {object} - État et fonctions pour gérer les conversations
 */
export const useConversation = (projectId) => {
  // État local
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Charger toutes les conversations du projet
   */
  const loadConversations = async () => {
    if (!projectId) return;

    try {
      setError(null);
      const response = await conversationAPI.listByProject(projectId);
      setConversations(response.data.conversations || []);
    } catch (err) {
      console.error('Erreur chargement conversations:', err);
      setError('Impossible de charger les conversations');
    }
  };

  /**
   * Créer une nouvelle conversation
   *
   * @param {string|null} title - Titre optionnel
   * @returns {object|null} - La conversation créée ou null en cas d'erreur
   */
  const createConversation = async (title = null) => {
    if (!projectId) {
      setError('Project ID requis pour créer une conversation');
      return null;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await conversationAPI.create(projectId, title);
      const newConv = response.data;

      // Ajouter au début de la liste
      setConversations(prev => [newConv, ...prev]);

      // Sélectionner automatiquement la nouvelle conversation
      setCurrentConversation(newConv);
      setMessages([]);

      return newConv;
    } catch (err) {
      console.error('Erreur création conversation:', err);
      setError('Impossible de créer la conversation');
      return null;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Charger une conversation existante et ses messages
   *
   * @param {number} conversationId - ID de la conversation
   */
  const loadConversation = async (conversationId) => {
    try {
      setLoading(true);
      setError(null);

      // Récupérer les messages
      const response = await conversationAPI.getMessages(conversationId);
      setMessages(response.data.messages || []);

      // Mettre à jour la conversation courante
      const conv = conversations.find(c => c.conversation_id === conversationId);
      if (conv) {
        setCurrentConversation(conv);
      }
    } catch (err) {
      console.error('Erreur chargement messages:', err);
      setError('Impossible de charger les messages');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Poser une question dans la conversation actuelle
   *
   * @param {string} question - La question à poser
   * @param {number} limit - Nombre de documents à récupérer (défaut: 5)
   * @returns {object|null} - La réponse ou null en cas d'erreur
   */
  const askQuestion = async (question, limit = 5) => {
    // Si pas de conversation, en créer une automatiquement
    let conversationId = currentConversation?.conversation_id;

    if (!conversationId) {
      const newConv = await createConversation();
      if (!newConv) {
        setError('Impossible de créer une conversation');
        return null;
      }
      conversationId = newConv.conversation_id;
    }

    try {
      setLoading(true);
      setError(null);

      // Ajouter optimistiquement la question à l'UI (pour réactivité immédiate)
      const userMessage = {
        message_id: Date.now(), // ID temporaire
        role: 'user',
        content: question,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);

      // Envoyer la question au backend
      const response = await nlpAPI.answer(projectId, {
        text: question,
        limit,
        conversation_id: conversationId
      });

      // Ajouter la réponse
      const assistantMessage = {
        message_id: Date.now() + 1, // ID temporaire
        role: 'assistant',
        content: response.data.answer,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Rafraîchir les conversations pour mettre à jour le titre si c'était la première question
      if (messages.length === 0) {
        await loadConversations();
      }

      return response.data;
    } catch (err) {
      console.error('Erreur lors de la question:', err);
      setError(err.response?.data?.detail || err.response?.data?.signal || 'Erreur lors de la génération de la réponse');

      // Retirer la question optimiste en cas d'erreur
      setMessages(prev => prev.slice(0, -1));

      return null;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Supprimer une conversation
   *
   * @param {number} conversationId - ID de la conversation à supprimer
   * @returns {boolean} - true si succès, false sinon
   */
  const deleteConversation = async (conversationId) => {
    try {
      setError(null);
      await conversationAPI.delete(conversationId);

      // Retirer de la liste
      setConversations(prev => prev.filter(c => c.conversation_id !== conversationId));

      // Si c'était la conversation courante, la désélectionner
      if (currentConversation?.conversation_id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }

      return true;
    } catch (err) {
      console.error('Erreur suppression conversation:', err);
      setError('Impossible de supprimer la conversation');
      return false;
    }
  };

  /**
   * Démarrer une nouvelle conversation (réinitialise l'état)
   */
  const startNewConversation = () => {
    setCurrentConversation(null);
    setMessages([]);
    setError(null);
  };

  // Charger les conversations au montage du composant
  useEffect(() => {
    if (projectId) {
      loadConversations();
    }
  }, [projectId]);

  // Retourner l'état et les fonctions
  return {
    // État
    conversations,
    currentConversation,
    messages,
    loading,
    error,

    // Actions
    createConversation,
    loadConversation,
    askQuestion,
    deleteConversation,
    startNewConversation,
    refreshConversations: loadConversations,

    // Helpers
    hasMessages: messages.length > 0,
    hasConversations: conversations.length > 0,
  };
};
