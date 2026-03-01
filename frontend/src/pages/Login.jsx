import { useState } from 'react'
import { Link } from 'react-router-dom'
import useAuthStore from '../stores/authStore'
import useNotificationStore from '../stores/notificationStore'

export default function Login() {
  const [email, setEmail] = useState('admin@crm-demo.com')
  const [password, setPassword] = useState('admin123')
  const { login, loading, error } = useAuthStore()
  const notify = useNotificationStore

  const handleSubmit = async (e) => {
    e.preventDefault()
    const result = await login(email, password)
    if (result.success) {
      notify.getState().success('Đăng nhập thành công')
    }
  }

  const demoAccounts = [
    { email: 'admin@crm-demo.com', password: 'admin123', role: 'Admin' },
    { email: 'staff@crm-demo.com', password: 'staff123', role: 'Staff' },
    { email: 'customer@crm-demo.com', password: 'customer123', role: 'Customer' }
  ]

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-600 mb-2">🤖 CRM AI Agent</h1>
          <p className="text-gray-600">Đăng nhập vào hệ thống</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mật khẩu
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 text-red-600 px-4 py-2 rounded-md text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            Chưa có tài khoản?{' '}
            <Link to="/register" className="text-blue-600 hover:text-blue-800 font-medium">
              Đăng ký ngay
            </Link>
          </p>
        </div>

        <div className="mt-6 pt-6 border-t">
          <p className="text-sm text-gray-600 font-medium mb-3">📝 Tài khoản demo:</p>
          <div className="space-y-2">
            {demoAccounts.map((account, index) => (
              <button
                key={index}
                onClick={() => { setEmail(account.email); setPassword(account.password) }}
                className="w-full text-left text-xs bg-gray-50 p-2 rounded border border-gray-200 hover:bg-blue-50 hover:border-blue-200 transition"
              >
                <div className="font-medium text-gray-700">{account.role}:</div>
                <div className="text-gray-600">
                  {account.email} / {account.password}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="mt-4 text-center text-xs text-gray-500">
          <p>🔧 Demo Mode - No OpenAI API required</p>
        </div>
      </div>
    </div>
  )
}
