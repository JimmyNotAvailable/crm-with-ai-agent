/**
 * Auth Store - Zustand
 * Manages authentication state: token, user, login/logout
 */
import { create } from 'zustand'
import { authAPI } from '../services/api'

const useAuthStore = create((set, get) => ({
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  loading: false,
  error: null,

  // Login
  login: async (email, password) => {
    set({ loading: true, error: null })
    try {
      const response = await authAPI.login(email, password)
      const { access_token, user } = response.data
      localStorage.setItem('token', access_token)
      if (user) localStorage.setItem('user', JSON.stringify(user))
      set({ token: access_token, user: user || null, loading: false })
      // Fetch user info if not returned with login
      if (!user) {
        get().fetchUser()
      }
      return { success: true }
    } catch (err) {
      const message = err.response?.data?.detail || 'Đăng nhập thất bại'
      set({ loading: false, error: message })
      return { success: false, error: message }
    }
  },

  // Register
  register: async (userData) => {
    set({ loading: true, error: null })
    try {
      const response = await authAPI.register(userData)
      const { access_token, user } = response.data
      localStorage.setItem('token', access_token)
      if (user) localStorage.setItem('user', JSON.stringify(user))
      set({ token: access_token, user: user || null, loading: false })
      if (!user) get().fetchUser()
      return { success: true }
    } catch (err) {
      const message = err.response?.data?.detail || 'Đăng ký thất bại'
      set({ loading: false, error: message })
      return { success: false, error: message }
    }
  },

  // Logout
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ token: null, user: null })
    // Don't need to call API - just clear locally
  },

  // Fetch current user info
  fetchUser: async () => {
    try {
      const response = await authAPI.getMe()
      const user = response.data
      localStorage.setItem('user', JSON.stringify(user))
      set({ user })
    } catch {
      // Token invalid -> logout
      get().logout()
    }
  },

  // Check if user has specific role
  hasRole: (role) => {
    const user = get().user
    if (!user) return false
    const userRole = user.role || user.user_type
    if (Array.isArray(role)) return role.includes(userRole)
    return userRole === role
  },

  // Check if user is staff or admin
  isStaffOrAdmin: () => {
    const user = get().user
    if (!user) return false
    const role = user.role || user.user_type
    return role === 'STAFF' || role === 'ADMIN'
  },

  clearError: () => set({ error: null }),
}))

export default useAuthStore
