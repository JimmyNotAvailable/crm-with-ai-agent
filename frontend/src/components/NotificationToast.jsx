/**
 * NotificationToast - Global toast notification display
 * Renders all active notifications from notificationStore
 */
import useNotificationStore from '../stores/notificationStore'

const typeStyles = {
  success: {
    bg: 'bg-green-50 border-green-400',
    text: 'text-green-800',
    icon: '✅',
  },
  error: {
    bg: 'bg-red-50 border-red-400',
    text: 'text-red-800',
    icon: '❌',
  },
  warning: {
    bg: 'bg-yellow-50 border-yellow-400',
    text: 'text-yellow-800',
    icon: '⚠️',
  },
  info: {
    bg: 'bg-blue-50 border-blue-400',
    text: 'text-blue-800',
    icon: 'ℹ️',
  },
}

export default function NotificationToast() {
  const { notifications, removeNotification } = useNotificationStore()

  if (notifications.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-[100] space-y-2 max-w-sm w-full">
      {notifications.map((n) => {
        const style = typeStyles[n.type] || typeStyles.info
        return (
          <div
            key={n.id}
            className={`flex items-start gap-3 p-4 rounded-lg border shadow-lg animate-slide-in ${style.bg}`}
          >
            <span className="text-lg flex-shrink-0">{style.icon}</span>
            <p className={`text-sm flex-1 ${style.text}`}>{n.message}</p>
            <button
              onClick={() => removeNotification(n.id)}
              className={`flex-shrink-0 text-lg leading-none hover:opacity-70 ${style.text}`}
            >
              ×
            </button>
          </div>
        )
      })}
    </div>
  )
}
