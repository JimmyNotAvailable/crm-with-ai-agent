/**
 * Notification Store - Zustand
 * Toast notification system replacing all alert() calls
 */
import { create } from 'zustand'

let notificationId = 0

const useNotificationStore = create((set, get) => ({
  notifications: [],

  /**
   * Add a notification
   * @param {'success'|'error'|'warning'|'info'} type
   * @param {string} message
   * @param {number} duration - auto-dismiss in ms (default 4000, 0 = no auto)
   */
  addNotification: (type, message, duration = 4000) => {
    const id = ++notificationId
    set((state) => ({
      notifications: [
        ...state.notifications,
        { id, type, message, createdAt: Date.now() }
      ]
    }))

    if (duration > 0) {
      setTimeout(() => {
        get().removeNotification(id)
      }, duration)
    }

    return id
  },

  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id)
    }))
  },

  // Convenience methods
  success: (message, duration) => get().addNotification('success', message, duration),
  error: (message, duration) => get().addNotification('error', message, duration || 6000),
  warning: (message, duration) => get().addNotification('warning', message, duration),
  info: (message, duration) => get().addNotification('info', message, duration),

  clearAll: () => set({ notifications: [] }),
}))

export default useNotificationStore
