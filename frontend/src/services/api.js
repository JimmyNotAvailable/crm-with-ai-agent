/**
 * Centralized API Service Layer
 * Uses Vite proxy (/api → http://localhost:8000) for all API calls
 * Provides typed methods for all backend endpoints
 */
import axios from 'axios'

// Create Axios instance using Vite proxy
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle 401 (auto-logout)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

// ==================== AUTH ====================
export const authAPI = {
  login: (email, password) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },

  register: (userData) => api.post('/auth/register', userData),

  getMe: () => api.get('/auth/me'),

  logout: () => api.post('/auth/logout'),

  updateProfile: (data) => api.put('/auth/me', data),
}

// ==================== PRODUCTS ====================
export const productsAPI = {
  getAll: (params = {}) => api.get('/products', { params }),

  getById: (id) => api.get(`/products/${id}`),

  create: (data) => api.post('/products', data),

  update: (id, data) => api.put(`/products/${id}`, data),

  delete: (id) => api.delete(`/products/${id}`),
}

// ==================== ORDERS ====================
export const ordersAPI = {
  getAll: (params = {}) => api.get('/orders/', { params }),

  getById: (id) => api.get(`/orders/${id}`),

  create: (data) => api.post('/orders/', data),

  update: (id, data) => api.put(`/orders/${id}`, data),

  cancel: (id) => api.delete(`/orders/${id}/cancel`),

  refund: (id, data) => api.post(`/orders/${id}/refund`, data),

  returnOrder: (id, data) => api.post(`/orders/${id}/return`, data),
}

// ==================== CART ====================
export const cartAPI = {
  get: () => api.get('/cart'),

  addItem: (productId, quantity = 1) =>
    api.post('/cart/items', { product_id: productId, quantity }),

  updateItem: (itemId, quantity) =>
    api.put(`/cart/items/${itemId}`, { quantity }),

  removeItem: (itemId) => api.delete(`/cart/items/${itemId}`),

  checkout: (data) => api.post('/cart/checkout', data),
}

// ==================== TICKETS ====================
export const ticketsAPI = {
  getAll: (params = {}) => api.get('/tickets', { params }),

  getById: (id) => api.get(`/tickets/${id}`),

  create: (data) => api.post('/tickets/', data),

  addMessage: (ticketId, message) =>
    api.post(`/tickets/${ticketId}/messages`, { message }),

  getSimilar: (ticketId) => api.get(`/tickets/${ticketId}/similar`),

  merge: (ticketId, data) => api.post(`/tickets/${ticketId}/merge`, data),

  update: (id, data) => api.put(`/tickets/${id}`, data),
}

// ==================== RAG / CHAT ====================
export const chatAPI = {
  send: (query, { conversationId, topK = 3, useCrmContext = true, actionId } = {}) => {
    const formData = new FormData()
    formData.append('query', query)
    formData.append('top_k', String(topK))
    formData.append('use_crm_context', String(useCrmContext))
    if (conversationId) formData.append('conversation_id', String(conversationId))
    if (actionId) formData.append('action_id', actionId)
    return api.post('/rag/chat', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  upload: (file, metadata = {}) => {
    const formData = new FormData()
    formData.append('file', file)
    if (metadata.title) formData.append('title', metadata.title)
    if (metadata.category) formData.append('category', metadata.category)
    return api.post('/rag/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
}

// ==================== KNOWLEDGE BASE ====================
export const kbAPI = {
  getAll: () => api.get('/kb'),

  getById: (id) => api.get(`/kb/${id}`),

  create: (formData) => api.post('/kb/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),

  update: (id, data) => api.put(`/kb/${id}`, data),

  delete: (id) => api.delete(`/kb/${id}`),

  reindex: (id) => api.post(`/kb/${id}/reindex`),

  healthCheck: () => api.get('/kb/health/check'),
}

// ==================== ANALYTICS ====================
export const analyticsAPI = {
  getDashboard: (days = 30) => api.get(`/analytics/dashboard?days=${days}`),

  getKPIOverview: () => api.get('/analytics/kpi/overview'),

  detectAnomalies: () => api.get('/analytics/anomalies/detect'),

  getRevenueTrend: (params = {}) => api.get('/analytics/revenue/trend', { params }),

  getOrderTrend: (params = {}) => api.get('/analytics/orders/trend', { params }),
}

// ==================== AI SUMMARIZATION ====================
export const summarizeAPI = {
  ticket: (ticketId) => api.get(`/ai/summarize/ticket/${ticketId}`),

  conversation: (conversationId) =>
    api.get(`/ai/summarize/conversation/${conversationId}`),

  customerBehavior: (userId) => api.get(`/ai/summarize/customer-behavior/${userId}`),

  batchTickets: (ticketIds) => api.post('/ai/summarize/tickets/batch', { ticket_ids: ticketIds }),
}

// ==================== PERSONALIZATION ====================
export const personalizationAPI = {
  getRecommendations: (params = {}) =>
    api.get('/ai/personalization/recommendations', { params }),

  getProfile: (userId) => api.get(`/ai/personalization/profile/${userId}`),
}

// ==================== AUDIT LOGS ====================
export const auditAPI = {
  getAll: (params = {}) => api.get('/audit', { params }),
}

// ==================== USERS (Admin) ====================
export const usersAPI = {
  getAll: (params = {}) => api.get('/auth/users', { params }),

  getById: (id) => api.get(`/auth/users/${id}`),

  update: (id, data) => api.put(`/auth/users/${id}`, data),

  delete: (id) => api.delete(`/auth/users/${id}`),
}

export default api
