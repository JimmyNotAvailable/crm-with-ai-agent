import { Link, useLocation } from 'react-router-dom'

export default function Layout({ children, onLogout }) {
  const location = useLocation()
  
  const isActive = (path) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold text-blue-600">🤖 CRM AI Agent</h1>
              <div className="flex space-x-4">
                <Link 
                  to="/products"
                  className={`px-4 py-2 rounded-md transition ${
                    isActive('/products') 
                      ? 'bg-blue-100 text-blue-700 font-medium' 
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  📦 Sản phẩm
                </Link>
                <Link 
                  to="/chat"
                  className={`px-4 py-2 rounded-md transition ${
                    isActive('/chat') 
                      ? 'bg-blue-100 text-blue-700 font-medium' 
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  💬 Chat AI
                </Link>
              </div>
            </div>
            <button
              onClick={onLogout}
              className="px-4 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600"
            >
              Đăng xuất
            </button>
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
