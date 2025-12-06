import axios from 'axios';

const API_URL = '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token à chaque requête
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour gérer les erreurs 401 (non authentifié)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getMe: () => api.get('/auth/me'),
  getAllUsers: () => api.get('/auth/users'),
};

export const dataAPI = {
  uploadFile: (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/data/upload/${projectId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  processData: (projectId, data) => api.post(`/data/process/${projectId}`, data),
  getProjectLanguage: (projectId) => api.get(`/data/project/${projectId}/language`),
  updateProjectLanguage: (projectId, language) => api.put(`/data/project/${projectId}/language`, { language }),
};

export const nlpAPI = {
  pushToIndex: (projectId, data) => api.post(`/nlp/index/push/${projectId}`, data),
  getIndexInfo: (projectId) => api.get(`/nlp/index/info/${projectId}`),
  search: (projectId, data) => api.post(`/nlp/index/search/${projectId}`, data),
  answer: (projectId, data) => api.post(`/nlp/index/answer/${projectId}`, data),
};

export const conversationAPI = {
  // Créer une nouvelle conversation
  create: (projectId, title = null) =>
    api.post('/conversations/create', { project_id: projectId, title }),

  // Lister les conversations d'un projet
  listByProject: (projectId, statusFilter = null) => {
    const params = statusFilter ? `?status_filter=${statusFilter}` : '';
    return api.get(`/conversations/project/${projectId}${params}`);
  },

  // Récupérer les messages d'une conversation
  getMessages: (conversationId, limit = 100) =>
    api.get(`/conversations/${conversationId}/messages?limit=${limit}`),

  // Supprimer une conversation
  delete: (conversationId) =>
    api.delete(`/conversations/${conversationId}`),
};

export const adminAPI = {
  // Projects
  getProjects: (page = 1, pageSize = 20) =>
    api.get(`/admin/projects?page=${page}&page_size=${pageSize}`),
  deleteProject: (projectId) =>
    api.delete(`/admin/projects/${projectId}`),
  updateProjectName: (projectId, projectName) =>
    api.patch(`/admin/projects/${projectId}/name`, { project_name: projectName }),

  // Assets
  getAssets: (page = 1, pageSize = 20, projectId = null, assetType = null) => {
    let url = `/admin/assets?page=${page}&page_size=${pageSize}`;
    if (projectId) url += `&project_id=${projectId}`;
    if (assetType) url += `&asset_type=${assetType}`;
    return api.get(url);
  },
  deleteAsset: (assetId) =>
    api.delete(`/admin/assets/${assetId}`),

  // Chunks
  getChunks: (page = 1, pageSize = 20, projectId = null, assetId = null) => {
    let url = `/admin/chunks?page=${page}&page_size=${pageSize}`;
    if (projectId) url += `&project_id=${projectId}`;
    if (assetId) url += `&asset_id=${assetId}`;
    return api.get(url);
  },
  deleteChunk: (chunkId) =>
    api.delete(`/admin/chunks/${chunkId}`),

  // Conversations
  getConversations: (page = 1, pageSize = 20, projectId = null, userId = null) => {
    let url = `/admin/conversations?page=${page}&page_size=${pageSize}`;
    if (projectId) url += `&project_id=${projectId}`;
    if (userId) url += `&user_id=${userId}`;
    return api.get(url);
  },
  deleteConversation: (conversationId) =>
    api.delete(`/admin/conversations/${conversationId}`),

  // Messages
  getMessages: (page = 1, pageSize = 20, conversationId = null) => {
    let url = `/admin/messages?page=${page}&page_size=${pageSize}`;
    if (conversationId) url += `&conversation_id=${conversationId}`;
    return api.get(url);
  },
  deleteMessage: (messageId) =>
    api.delete(`/admin/messages/${messageId}`),

  // Vector Collections
  getVectorCollections: () =>
    api.get('/admin/vectors/collections'),
  getCollectionVectors: (collectionName, page = 1, pageSize = 20) =>
    api.get(`/admin/vectors/collections/${collectionName}?page=${page}&page_size=${pageSize}`),
  deleteCollection: (collectionName) =>
    api.delete(`/admin/vectors/collections/${collectionName}`),

  // Exchange Rates Admin
  getSchedulerStatus: () =>
    api.get('/exchange-rates/admin/scheduler/status'),
  fetchRatesNow: () =>
    api.post('/exchange-rates/admin/fetch-rates-now'),
  trainExchangeModel: (currencyPair, daysHistory) =>
    api.post(`/exchange-rates/admin/train-model?currency_pair=${currencyPair}&days_history=${daysHistory}`),
  generatePredictions: (currencyPair, daysAhead) =>
    api.post(`/exchange-rates/admin/generate-predictions?currency_pair=${currencyPair}&days_ahead=${daysAhead}`),
};

export const publicAPI = {
  // Exchange Rates Public (for authenticated users)
  getLatestExchangeRates: () =>
    api.get('/exchange-rates/latest'),
  getExchangePredictions: (currencyPair, daysHistory = 30, daysAhead = 7) =>
    api.get(`/exchange-rates/predictions?currency_pair=${encodeURIComponent(currencyPair)}&days_history=${daysHistory}&days_ahead=${daysAhead}`),
  getExchangeHistory: (currencyPair, days = 365) =>
    api.get(`/exchange-rates/history?currency_pair=${encodeURIComponent(currencyPair)}&days=${days}`),
};

export default api;
