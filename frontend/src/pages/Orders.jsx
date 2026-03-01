/**
 * Orders Page - Order History
 * View and track all orders with status filtering
 */
import { useState, useEffect, useMemo } from 'react'
import { ordersAPI } from '../services/api'
import useNotificationStore from '../stores/notificationStore'
import Pagination from '../components/Pagination'

const ORDER_PAGE_SIZE = 10

const statusLabels = {
  PENDING: { label: 'Chờ xử lý', color: 'bg-yellow-100 text-yellow-800' },
  CONFIRMED: { label: 'Đã xác nhận', color: 'bg-blue-100 text-blue-800' },
  PROCESSING: { label: 'Đang xử lý', color: 'bg-indigo-100 text-indigo-800' },
  SHIPPED: { label: 'Đang giao', color: 'bg-purple-100 text-purple-800' },
  DELIVERED: { label: 'Đã giao', color: 'bg-green-100 text-green-800' },
  CANCELLED: { label: 'Đã hủy', color: 'bg-red-100 text-red-800' },
  REFUNDED: { label: 'Hoàn tiền', color: 'bg-gray-100 text-gray-800' },
}

const formatPrice = (price) =>
  new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price)

const formatDate = (dateStr) =>
  dateStr ? new Date(dateStr).toLocaleDateString('vi-VN', {
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  }) : '-'

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedOrder, setSelectedOrder] = useState(null)
  const [confirmCancelId, setConfirmCancelId] = useState(null)
  const [statusFilter, setStatusFilter] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const notify = useNotificationStore

  useEffect(() => {
    fetchOrders()
    setCurrentPage(1)
  }, [statusFilter])

  const fetchOrders = async () => {
    setLoading(true)
    try {
      const params = { limit: 50 }
      if (statusFilter) params.status = statusFilter
      const response = await ordersAPI.getAll(params)
      setOrders(response.data)
    } catch (err) {
      notify.getState().error('Không thể tải danh sách đơn hàng')
    } finally {
      setLoading(false)
    }
  }

  const fetchOrderDetail = async (orderId) => {
    try {
      const response = await ordersAPI.getById(orderId)
      setSelectedOrder(response.data)
    } catch {
      notify.getState().error('Không thể tải chi tiết đơn hàng')
    }
  }

  const handleCancel = async (orderId) => {
    try {
      await ordersAPI.cancel(orderId)
      notify.getState().success('Đã hủy đơn hàng thành công')
      setConfirmCancelId(null)
      setSelectedOrder(null)
      fetchOrders()
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể hủy đơn hàng')
    }
  }

  const getStatusBadge = (status) => {
    const s = statusLabels[status] || { label: status, color: 'bg-gray-100 text-gray-800' }
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${s.color}`}>
        {s.label}
      </span>
    )
  }

  const totalOrderPages = Math.ceil(orders.length / ORDER_PAGE_SIZE)
  const paginatedOrders = useMemo(() => {
    const start = (currentPage - 1) * ORDER_PAGE_SIZE
    return orders.slice(start, start + ORDER_PAGE_SIZE)
  }, [orders, currentPage])

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Đang tải đơn hàng...</p>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">📦 Lịch Sử Đơn Hàng</h2>
          <p className="text-gray-600 mt-1">Theo dõi và quản lý đơn hàng của bạn</p>
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Tất cả trạng thái</option>
          {Object.entries(statusLabels).map(([key, val]) => (
            <option key={key} value={key}>{val.label}</option>
          ))}
        </select>
      </div>

      {/* Order Detail Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-xl font-bold text-gray-800">
                  Đơn hàng #{selectedOrder.order_number}
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  Ngày đặt: {formatDate(selectedOrder.created_at)}
                </p>
              </div>
              <button
                onClick={() => setSelectedOrder(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="flex gap-2 mb-6">
              {getStatusBadge(selectedOrder.status)}
              {selectedOrder.payment_method && (
                <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-50 text-blue-700">
                  {selectedOrder.payment_method}
                </span>
              )}
            </div>

            {/* Order Items */}
            <div className="mb-6">
              <h4 className="font-semibold text-gray-700 mb-3">Sản phẩm</h4>
              <div className="space-y-3">
                {selectedOrder.items?.map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center bg-gray-50 p-3 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-800">{item.product_name}</p>
                      <p className="text-sm text-gray-500">SKU: {item.product_sku} | SL: {item.quantity}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">{formatPrice(item.unit_price)} × {item.quantity}</p>
                      <p className="font-bold text-blue-600">{formatPrice(item.subtotal)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Shipping Info */}
            {selectedOrder.shipping_address && (
              <div className="mb-6 bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-700 mb-2">Thông tin giao hàng</h4>
                <p className="text-sm text-gray-600">{selectedOrder.shipping_address}</p>
                {selectedOrder.shipping_city && (
                  <p className="text-sm text-gray-600">{selectedOrder.shipping_city}</p>
                )}
                {selectedOrder.shipping_phone && (
                  <p className="text-sm text-gray-600">SĐT: {selectedOrder.shipping_phone}</p>
                )}
              </div>
            )}

            {/* Total */}
            <div className="border-t pt-4 flex justify-between items-center mb-6">
              <span className="text-lg font-bold">Tổng cộng:</span>
              <span className="text-2xl font-bold text-blue-600">
                {formatPrice(selectedOrder.total_amount)}
              </span>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              {(selectedOrder.status === 'PENDING' || selectedOrder.status === 'CONFIRMED') && (
                confirmCancelId === selectedOrder.id ? (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">Xác nhận hủy?</span>
                    <button onClick={() => handleCancel(selectedOrder.id)} className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600">Hủy đơn</button>
                    <button onClick={() => setConfirmCancelId(null)} className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300">Không</button>
                  </div>
                ) : (
                  <button
                    onClick={() => setConfirmCancelId(selectedOrder.id)}
                    className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
                  >
                    Hủy đơn hàng
                  </button>
                )
              )}
              <button
                onClick={() => setSelectedOrder(null)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Orders Table */}
      {orders.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <div className="text-6xl mb-4">📦</div>
          <p className="text-xl text-gray-600">Chưa có đơn hàng nào</p>
          <p className="text-gray-500 mt-2">Hãy khám phá sản phẩm và đặt hàng ngay!</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mã đơn</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ngày đặt</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thanh toán</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tổng tiền</th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {paginatedOrders.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {order.order_number}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatDate(order.created_at)}
                  </td>
                  <td className="px-6 py-4">{getStatusBadge(order.status)}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {order.payment_method || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm font-bold text-blue-600 text-right">
                    {formatPrice(order.total_amount)}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <button
                      onClick={() => fetchOrderDetail(order.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      Chi tiết
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination
        currentPage={currentPage}
        totalPages={totalOrderPages}
        totalItems={orders.length}
        pageSize={ORDER_PAGE_SIZE}
        onPageChange={setCurrentPage}
      />
    </div>
  )
}
