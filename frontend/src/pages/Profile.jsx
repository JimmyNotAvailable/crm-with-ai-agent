/**
 * User Profile Page
 * View and edit user profile information
 */
import { useState, useEffect } from 'react'
import useAuthStore from '../stores/authStore'
import { authAPI } from '../services/api'
import useNotificationStore from '../stores/notificationStore'

export default function Profile() {
  const { user, fetchUser } = useAuthStore()
  const notify = useNotificationStore
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
  })
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        phone: user.phone || '',
      })
    }
  }, [user])

  const handleSaveProfile = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await authAPI.updateProfile(formData)
      await fetchUser()
      setEditing(false)
      notify.getState().success('Cập nhật thông tin thành công')
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể cập nhật thông tin')
    } finally {
      setSaving(false)
    }
  }

  const handleChangePassword = async (e) => {
    e.preventDefault()
    if (passwordData.new_password !== passwordData.confirm_password) {
      notify.getState().error('Mật khẩu xác nhận không khớp')
      return
    }
    if (passwordData.new_password.length < 6) {
      notify.getState().error('Mật khẩu mới phải có ít nhất 6 ký tự')
      return
    }
    setSaving(true)
    try {
      await authAPI.updateProfile({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      })
      setShowPasswordForm(false)
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' })
      notify.getState().success('Đổi mật khẩu thành công')
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể đổi mật khẩu')
    } finally {
      setSaving(false)
    }
  }

  const getRoleBadge = (role) => {
    const roles = {
      ADMIN: { label: 'Quản trị viên', color: 'bg-red-100 text-red-800' },
      STAFF: { label: 'Nhân viên', color: 'bg-blue-100 text-blue-800' },
      CUSTOMER: { label: 'Khách hàng', color: 'bg-green-100 text-green-800' },
    }
    const r = roles[role] || { label: role, color: 'bg-gray-100 text-gray-800' }
    return (
      <span className={`px-3 py-1 text-sm font-medium rounded-full ${r.color}`}>
        {r.label}
      </span>
    )
  }

  if (!user) {
    return (
      <div className="text-center py-12 text-gray-600">
        Đang tải thông tin người dùng...
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">👤 Hồ Sơ Cá Nhân</h2>

      {/* Profile Card */}
      <div className="bg-white rounded-lg shadow-md p-8 mb-6">
        <div className="flex items-center gap-6 mb-8">
          <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center text-3xl font-bold text-blue-600">
            {(user.full_name || user.email)?.[0]?.toUpperCase() || '?'}
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-800">{user.full_name || 'Chưa cập nhật'}</h3>
            <p className="text-gray-500">{user.email}</p>
            <div className="mt-2">
              {getRoleBadge(user.role || user.user_type)}
            </div>
          </div>
        </div>

        {!editing ? (
          <>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-500">Họ và tên</p>
                  <p className="text-gray-800">{user.full_name || '-'}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Email</p>
                  <p className="text-gray-800">{user.email}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Số điện thoại</p>
                  <p className="text-gray-800">{user.phone || '-'}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Ngày tạo</p>
                  <p className="text-gray-800">
                    {user.created_at
                      ? new Date(user.created_at).toLocaleDateString('vi-VN')
                      : '-'}
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-6 flex gap-3">
              <button
                onClick={() => setEditing(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                ✏️ Chỉnh sửa
              </button>
              <button
                onClick={() => setShowPasswordForm(!showPasswordForm)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                🔒 Đổi mật khẩu
              </button>
            </div>
          </>
        ) : (
          <form onSubmit={handleSaveProfile} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Họ và tên</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
              >
                {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
              </button>
              <button
                type="button"
                onClick={() => setEditing(false)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                Hủy
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Change Password Form */}
      {showPasswordForm && (
        <div className="bg-white rounded-lg shadow-md p-8">
          <h3 className="text-lg font-bold text-gray-800 mb-4">🔒 Đổi Mật Khẩu</h3>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mật khẩu hiện tại</label>
              <input
                type="password"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mật khẩu mới</label>
              <input
                type="password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                required
                minLength={6}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Xác nhận mật khẩu mới</label>
              <input
                type="password"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
              >
                {saving ? 'Đang xử lý...' : 'Đổi mật khẩu'}
              </button>
              <button
                type="button"
                onClick={() => setShowPasswordForm(false)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                Hủy
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
