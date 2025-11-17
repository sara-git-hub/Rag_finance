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
};

export const nlpAPI = {
  pushToIndex: (projectId, data) => api.post(`/nlp/index/push/${projectId}`, data),
  getIndexInfo: (projectId) => api.get(`/nlp/index/info/${projectId}`),
  search: (projectId, data) => api.post(`/nlp/index/search/${projectId}`, data),
  answer: (projectId, data) => api.post(`/nlp/index/answer/${projectId}`, data),
};

export default api;
