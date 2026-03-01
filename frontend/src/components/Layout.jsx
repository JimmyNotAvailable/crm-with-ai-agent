import { Link, useLocation } from 'react-router-dom'
import useAuthStore from '../stores/authStore'

export default function Layout({ children, onLogout }) {
  const location = useLocation()
  const { user } = useAuthStore()
  
  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/')
  const userRole = user?.role || user?.user_type || 'CUSTOMER'
  const isStaff = userRole === 'STAFF' || userRole === 'ADMIN'

  const navLink = (to, label, show = true) => {
    if (!show) return null
    return (
      <Link
        to={to}
        className={`px-3 py-2 rounded-md transition text-sm ${
          isActive(to)
            ? 'bg-blue-100 text-blue-700 font-medium'
            : 'text-gray-600 hover:bg-gray-100'
        }`}
      >
        {label}
      </Link>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-6">
              <Link to="/" className="text-xl font-bold text-blue-600">🤖 CRM AI Agent</Link>
              <div className="flex space-x-1">
                {navLink('/dashboard', '📊 Dashboard', isStaff)}
                {navLink('/products', '📦 Sản phẩm')}
                {navLink('/cart', '🛒 Giỏ hàng')}
                {navLink('/orders', '📋 Đơn hàng')}
                {navLink('/tickets', '🎫 Hỗ trợ')}
                {navLink('/chat', '💬 Chat AI')}
                {navLink('/kb', '📚 Tri thức', isStaff)}
                {navLink('/admin', '⚙️ Quản trị', isStaff)}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/profile"
                className="flex items-center space-x-2 text-sm text-gray-600 hover:text-blue-600"
              >
                <span className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">
                  {(user?.full_name || user?.email)?.[0]?.toUpperCase() || '?'}
                </span>
                <span className="hidden md:block">{user?.full_name || user?.email || 'User'}</span>
              </Link>
              <button
                onClick={onLogout}
                className="px-3 py-1.5 text-sm bg-red-500 text-white rounded-md hover:bg-red-600"
              >
                Đăng xuất
              </button>
            </div>
          </div>
        </div>
      </nav>
      
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      <footer className="bg-white border-t mt-auto">
        <div className="container mx-auto px-4 py-4 text-center text-sm text-gray-600">
          <p>CRM AI Agent Demo - Powered by FastAPI + React</p>
          <p className="text-xs text-gray-500 mt-1">🔧 Demo Mode: Mock LLM Enabled</p>
        </div>
      </footer>
    </div>
  )
}
