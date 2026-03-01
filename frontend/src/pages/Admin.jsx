/**
 * Admin Panel
 * Users, Products, Orders, Tickets management (STAFF/ADMIN only)
 */
import { useState, useEffect } from 'react'
import { productsAPI, ordersAPI, ticketsAPI, usersAPI } from '../services/api'
import useNotificationStore from '../stores/notificationStore'
import useAuthStore from '../stores/authStore'

const TABS = [
  { key: 'users', label: '👥 Người dùng', roles: ['ADMIN'] },
  { key: 'products', label: '📦 Sản phẩm', roles: ['ADMIN', 'STAFF'] },
  { key: 'orders', label: '📋 Đơn hàng', roles: ['ADMIN', 'STAFF'] },
  { key: 'tickets', label: '🎫 Tickets', roles: ['ADMIN', 'STAFF'] },
]

export default function Admin() {
  const [activeTab, setActiveTab] = useState('products')
  const { user } = useAuthStore()
  const notify = useNotificationStore

  const userRole = user?.role || user?.user_type || 'CUSTOMER'
  const visibleTabs = TABS.filter(t => t.roles.includes(userRole))

  useEffect(() => {
    // Default to first visible tab
    if (visibleTabs.length > 0 && !visibleTabs.find(t => t.key === activeTab)) {
      setActiveTab(visibleTabs[0].key)
    }
  }, [userRole])

  if (!['ADMIN', 'STAFF'].includes(userRole)) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🔒</div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Truy cập bị từ chối</h2>
        <p className="text-gray-600">Bạn cần quyền ADMIN hoặc STAFF để truy cập trang này.</p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">⚙️ Quản Trị Hệ Thống</h2>
        <p className="text-gray-600 mt-1">Quản lý người dùng, sản phẩm, đơn hàng và tickets</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 rounded-lg p-1 w-fit">
        {visibleTabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 text-sm font-medium rounded-md transition ${
              activeTab === tab.key
                ? 'bg-white text-blue-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'users' && <UsersTab />}
      {activeTab === 'products' && <ProductsTab />}
      {activeTab === 'orders' && <OrdersTab />}
      {activeTab === 'tickets' && <TicketsTab />}
    </div>
  )
}

// ==================== USERS TAB ====================
function UsersTab() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const notify = useNotificationStore

  useEffect(() => { fetchUsers() }, [])

  const fetchUsers = async () => {
    try {
      const res = await usersAPI.getAll()
      setUsers(Array.isArray(res.data) ? res.data : [])
    } catch {
      notify.getState().error('Không thể tải danh sách người dùng')
    } finally {
      setLoading(false)
    }
  }

  const handleRoleChange = async (userId, newRole) => {
    try {
      await usersAPI.update(userId, { role: newRole })
      notify.getState().success('Cập nhật vai trò thành công')
      fetchUsers()
    } catch {
      notify.getState().error('Không thể cập nhật vai trò')
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tên</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vai trò</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ngày tạo</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thao tác</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {users.map(u => (
            <tr key={u.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 text-sm font-medium text-gray-900">{u.full_name || '-'}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{u.email}</td>
              <td className="px-6 py-4">
                <select
                  value={u.role || u.user_type || 'CUSTOMER'}
                  onChange={(e) => handleRoleChange(u.id, e.target.value)}
                  className="text-sm border border-gray-300 rounded px-2 py-1"
                >
                  <option value="CUSTOMER">Customer</option>
                  <option value="STAFF">Staff</option>
                  <option value="ADMIN">Admin</option>
                </select>
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                {u.created_at ? new Date(u.created_at).toLocaleDateString('vi-VN') : '-'}
              </td>
              <td className="px-6 py-4 text-sm">
                <span className={`px-2 py-1 rounded-full text-xs ${
                  u.is_active !== false ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {u.is_active !== false ? 'Active' : 'Inactive'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {users.length === 0 && (
        <div className="text-center py-8 text-gray-500">Không có người dùng nào</div>
      )}
    </div>
  )
}

// ==================== PRODUCTS TAB ====================
function ProductsTab() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [editModal, setEditModal] = useState(null) // null or product object
  const [confirmDeleteId, setConfirmDeleteId] = useState(null)
  const [formData, setFormData] = useState({
    name: '', price: '', stock_quantity: '', category: '', sku: '', description: ''
  })
  const notify = useNotificationStore

  useEffect(() => { fetchProducts() }, [])

  const fetchProducts = async () => {
    try {
      const res = await productsAPI.getAll()
      setProducts(Array.isArray(res.data) ? res.data : [])
    } catch {
      notify.getState().error('Không thể tải sản phẩm')
    } finally {
      setLoading(false)
    }
  }

  const openEdit = (product = null) => {
    if (product) {
      setFormData({
        name: product.name || '',
        price: product.price || '',
        stock_quantity: product.stock_quantity ?? '',
        category: product.category || '',
        sku: product.sku || '',
        description: product.description || ''
      })
    } else {
      setFormData({ name: '', price: '', stock_quantity: '', category: '', sku: '', description: '' })
    }
    setEditModal(product || 'new')
  }

  const handleSave = async (e) => {
    e.preventDefault()
    const data = {
      ...formData,
      price: parseFloat(formData.price),
      stock_quantity: parseInt(formData.stock_quantity) || 0
    }
    try {
      if (editModal === 'new') {
        await productsAPI.create(data)
        notify.getState().success('Tạo sản phẩm thành công')
      } else {
        await productsAPI.update(editModal.id, data)
        notify.getState().success('Cập nhật sản phẩm thành công')
      }
      setEditModal(null)
      fetchProducts()
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Lỗi khi lưu sản phẩm')
    }
  }

  const handleDelete = async (id) => {
    try {
      await productsAPI.delete(id)
      notify.getState().success('Đã xóa sản phẩm')
      setConfirmDeleteId(null)
      fetchProducts()
    } catch {
      notify.getState().error('Không thể xóa sản phẩm')
    }
  }

  const formatPrice = (p) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(p)

  if (loading) return <LoadingSpinner />

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <p className="text-sm text-gray-600">Tổng: {products.length} sản phẩm</p>
        <button
          onClick={() => openEdit()}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
        >
          + Thêm sản phẩm
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tên</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Danh mục</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Giá</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kho</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thao tác</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {products.map(p => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-500">{p.sku}</td>
                <td className="px-4 py-3 text-sm font-medium text-gray-900 max-w-xs truncate">{p.name}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{p.category || '-'}</td>
                <td className="px-4 py-3 text-sm text-blue-600 font-medium">{formatPrice(p.price)}</td>
                <td className="px-4 py-3 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    p.stock_quantity > 20 ? 'bg-green-100 text-green-700'
                    : p.stock_quantity > 0 ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-red-100 text-red-700'
                  }`}>
                    {p.stock_quantity}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm space-x-2 relative">
                  <button onClick={() => openEdit(p)} className="text-blue-600 hover:text-blue-800">✏️</button>
                  <button onClick={() => setConfirmDeleteId(p.id)} className="text-red-600 hover:text-red-800">🗑️</button>
                  {confirmDeleteId === p.id && (
                    <div className="absolute right-4 top-1 bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-10">
                      <p className="text-xs text-gray-700 mb-2">Xóa sản phẩm?</p>
                      <div className="flex gap-2">
                        <button onClick={() => handleDelete(p.id)} className="px-2 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600">Xóa</button>
                        <button onClick={() => setConfirmDeleteId(null)} className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded hover:bg-gray-300">Hủy</button>
                      </div>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Edit/Create Modal */}
      {editModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
            <h3 className="text-lg font-bold mb-4">
              {editModal === 'new' ? '➕ Thêm sản phẩm' : '✏️ Sửa sản phẩm'}
            </h3>
            <form onSubmit={handleSave} className="space-y-3">
              <input
                type="text" placeholder="Tên sản phẩm *" required
                value={formData.name}
                onChange={e => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
              />
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="text" placeholder="SKU *" required
                  value={formData.sku}
                  onChange={e => setFormData({ ...formData, sku: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md"
                />
                <input
                  type="text" placeholder="Danh mục"
                  value={formData.category}
                  onChange={e => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="number" placeholder="Giá *" required min="0"
                  value={formData.price}
                  onChange={e => setFormData({ ...formData, price: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md"
                />
                <input
                  type="number" placeholder="Số lượng kho" min="0"
                  value={formData.stock_quantity}
                  onChange={e => setFormData({ ...formData, stock_quantity: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
              <textarea
                placeholder="Mô tả sản phẩm" rows="3"
                value={formData.description}
                onChange={e => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
              />
              <div className="flex gap-3">
                <button type="submit" className="flex-1 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700">
                  Lưu
                </button>
                <button type="button" onClick={() => setEditModal(null)} className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-md hover:bg-gray-300">
                  Hủy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}

// ==================== ORDERS TAB ====================
function OrdersTab() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const notify = useNotificationStore

  useEffect(() => { fetchOrders() }, [statusFilter])

  const fetchOrders = async () => {
    try {
      const params = statusFilter ? { status: statusFilter } : {}
      const res = await ordersAPI.getAll(params)
      setOrders(Array.isArray(res.data) ? res.data : [])
    } catch {
      notify.getState().error('Không thể tải đơn hàng')
    } finally {
      setLoading(false)
    }
  }

  const handleStatusUpdate = async (orderId, status) => {
    try {
      await ordersAPI.update(orderId, { status })
      notify.getState().success('Cập nhật trạng thái thành công')
      fetchOrders()
    } catch {
      notify.getState().error('Không thể cập nhật trạng thái')
    }
  }

  const formatPrice = (p) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(p)

  const STATUS_OPTIONS = ['PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED']
  const statusColors = {
    PENDING: 'bg-yellow-100 text-yellow-800',
    CONFIRMED: 'bg-blue-100 text-blue-800',
    PROCESSING: 'bg-indigo-100 text-indigo-800',
    SHIPPED: 'bg-purple-100 text-purple-800',
    DELIVERED: 'bg-green-100 text-green-800',
    CANCELLED: 'bg-red-100 text-red-800',
    REFUNDED: 'bg-gray-100 text-gray-800',
  }

  if (loading) return <LoadingSpinner />

  return (
    <>
      <div className="flex items-center gap-3 mb-4">
        <select
          value={statusFilter}
          onChange={e => { setStatusFilter(e.target.value); setLoading(true) }}
          className="px-3 py-2 border rounded-md text-sm"
        >
          <option value="">Tất cả trạng thái</option>
          {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <span className="text-sm text-gray-600">Tổng: {orders.length} đơn</span>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mã đơn</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Khách hàng</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tổng tiền</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ngày tạo</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cập nhật</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {orders.map(o => (
              <tr key={o.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{o.order_number}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{o.customer_name || o.customer_id}</td>
                <td className="px-4 py-3 text-sm font-medium text-blue-600">{formatPrice(o.total_amount)}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[o.status] || 'bg-gray-100'}`}>
                    {o.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {o.created_at ? new Date(o.created_at).toLocaleDateString('vi-VN') : '-'}
                </td>
                <td className="px-4 py-3">
                  <select
                    value={o.status}
                    onChange={e => handleStatusUpdate(o.id, e.target.value)}
                    className="text-xs border rounded px-2 py-1"
                  >
                    {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {orders.length === 0 && (
          <div className="text-center py-8 text-gray-500">Không có đơn hàng nào</div>
        )}
      </div>
    </>
  )
}

// ==================== TICKETS TAB ====================
function TicketsTab() {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const notify = useNotificationStore

  useEffect(() => { fetchTickets() }, [])

  const fetchTickets = async () => {
    try {
      const res = await ticketsAPI.getAll()
      setTickets(Array.isArray(res.data) ? res.data : [])
    } catch {
      notify.getState().error('Không thể tải tickets')
    } finally {
      setLoading(false)
    }
  }

  const handleStatusUpdate = async (ticketId, status) => {
    try {
      await ticketsAPI.update(ticketId, { status })
      notify.getState().success('Cập nhật trạng thái ticket thành công')
      fetchTickets()
    } catch {
      notify.getState().error('Không thể cập nhật trạng thái')
    }
  }

  const statusColors = {
    OPEN: 'bg-blue-100 text-blue-800',
    IN_PROGRESS: 'bg-yellow-100 text-yellow-800',
    WAITING_CUSTOMER: 'bg-purple-100 text-purple-800',
    RESOLVED: 'bg-green-100 text-green-800',
    CLOSED: 'bg-gray-100 text-gray-800',
  }

  const priorityColors = {
    LOW: 'bg-gray-100 text-gray-600',
    MEDIUM: 'bg-blue-100 text-blue-600',
    HIGH: 'bg-orange-100 text-orange-600',
    URGENT: 'bg-red-100 text-red-600',
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mã</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tiêu đề</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Danh mục</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ưu tiên</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cập nhật</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {tickets.map(t => (
            <tr key={t.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-sm font-medium text-gray-900">#{t.ticket_number}</td>
              <td className="px-4 py-3 text-sm text-gray-800 max-w-xs truncate">{t.subject}</td>
              <td className="px-4 py-3 text-sm text-gray-600">{t.category}</td>
              <td className="px-4 py-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${priorityColors[t.priority] || 'bg-gray-100'}`}>
                  {t.priority}
                </span>
              </td>
              <td className="px-4 py-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[t.status] || 'bg-gray-100'}`}>
                  {t.status}
                </span>
              </td>
              <td className="px-4 py-3">
                <select
                  value={t.status}
                  onChange={e => handleStatusUpdate(t.id, e.target.value)}
                  className="text-xs border rounded px-2 py-1"
                >
                  <option value="OPEN">OPEN</option>
                  <option value="IN_PROGRESS">IN_PROGRESS</option>
                  <option value="WAITING_CUSTOMER">WAITING_CUSTOMER</option>
                  <option value="RESOLVED">RESOLVED</option>
                  <option value="CLOSED">CLOSED</option>
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {tickets.length === 0 && (
        <div className="text-center py-8 text-gray-500">Không có ticket nào</div>
      )}
    </div>
  )
}

// ==================== SHARED COMPONENTS ====================
function LoadingSpinner() {
  return (
    <div className="text-center py-12">
      <div className="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      <p className="mt-3 text-gray-600">Đang tải...</p>
    </div>
  )
}
