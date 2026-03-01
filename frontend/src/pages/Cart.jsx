import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { cartAPI } from '../services/api';
import useNotificationStore from '../stores/notificationStore';

const Cart = () => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [checkingOut, setCheckingOut] = useState(false);
  const [showCheckoutForm, setShowCheckoutForm] = useState(false);
  const [confirmRemoveId, setConfirmRemoveId] = useState(null);
  const navigate = useNavigate();
  const notify = useNotificationStore;

  const [checkoutData, setCheckoutData] = useState({
    shipping_address: '',
    shipping_city: '',
    shipping_phone: '',
    payment_method: 'COD',
    customer_notes: ''
  });

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await cartAPI.get();
      setCart(response.data);
    } catch (err) {
      setError('Không thể tải giỏ hàng');
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId, newQuantity) => {
    if (newQuantity < 1) return;
    
    try {
      await cartAPI.updateItem(itemId, newQuantity);
      fetchCart();
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể cập nhật');
    }
  };

  const removeItem = async (itemId) => {
    try {
      await cartAPI.removeItem(itemId);
      setConfirmRemoveId(null);
      fetchCart();
      notify.getState().success('Đã xóa sản phẩm khỏi giỏ hàng');
    } catch (err) {
      notify.getState().error('Không thể xóa sản phẩm');
    }
  };

  const handleCheckout = async (e) => {
    e.preventDefault();
    setCheckingOut(true);
    
    try {
      const response = await cartAPI.checkout(checkoutData);
      const order = response.data;
      notify.getState().success(`Đặt hàng thành công! Mã đơn: ${order.order_number}`);
      setShowCheckoutForm(false);
      fetchCart();
      navigate('/orders');
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể đặt hàng');
    } finally {
      setCheckingOut(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-gray-600">Đang tải giỏ hàng...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">🛒 Giỏ Hàng Của Bạn</h1>

      {/* Checkout Form Modal */}
      {showCheckoutForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
            <h2 className="text-2xl font-bold mb-4">Thông Tin Giao Hàng</h2>
            <form onSubmit={handleCheckout}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Địa chỉ giao hàng *
                </label>
                <input
                  type="text"
                  required
                  value={checkoutData.shipping_address}
                  onChange={(e) => setCheckoutData({ ...checkoutData, shipping_address: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Số nhà, tên đường..."
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Thành phố *
                </label>
                <input
                  type="text"
                  required
                  value={checkoutData.shipping_city}
                  onChange={(e) => setCheckoutData({ ...checkoutData, shipping_city: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Hà Nội, TP.HCM..."
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Số điện thoại *
                </label>
                <input
                  type="tel"
                  required
                  value={checkoutData.shipping_phone}
                  onChange={(e) => setCheckoutData({ ...checkoutData, shipping_phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="0901234567"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phương thức thanh toán
                </label>
                <select
                  value={checkoutData.payment_method}
                  onChange={(e) => setCheckoutData({ ...checkoutData, payment_method: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="COD">Thanh toán khi nhận hàng (COD)</option>
                  <option value="BANK_TRANSFER">Chuyển khoản ngân hàng</option>
                  <option value="CREDIT_CARD">Thẻ tín dụng</option>
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ghi chú (Tùy chọn)
                </label>
                <textarea
                  value={checkoutData.customer_notes}
                  onChange={(e) => setCheckoutData({ ...checkoutData, customer_notes: e.target.value })}
                  rows="3"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Ghi chú cho người bán..."
                />
              </div>

              <div className="bg-blue-50 p-4 rounded-lg mb-4">
                <div className="flex justify-between items-center text-lg font-bold">
                  <span>Tổng thanh toán:</span>
                  <span className="text-blue-600">{formatPrice(cart?.total_amount || 0)}</span>
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={checkingOut}
                  className="flex-1 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white py-3 rounded-lg font-medium"
                >
                  {checkingOut ? 'Đang xử lý...' : '✓ Xác Nhận Đặt Hàng'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCheckoutForm(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-3 rounded-lg font-medium"
                >
                  Hủy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Cart Content */}
      {!cart || cart.items.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <div className="text-6xl mb-4">🛒</div>
          <p className="text-xl text-gray-600 mb-4">Giỏ hàng của bạn đang trống</p>
          <button
            onClick={() => navigate('/products')}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
          >
            Tiếp tục mua sắm
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {cart.items.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow p-6 relative">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-1">
                      {item.product_name}
                    </h3>
                    <p className="text-sm text-gray-500 mb-2">SKU: {item.product_sku}</p>
                    <p className="text-blue-600 font-bold">{formatPrice(item.unit_price)}</p>
                  </div>

                  <button
                    onClick={() => setConfirmRemoveId(item.id)}
                    className="text-red-500 hover:text-red-700 text-xl ml-4"
                  >
                    🗑️
                  </button>
                  {confirmRemoveId === item.id && (
                    <div className="absolute right-6 top-6 bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-10">
                      <p className="text-sm text-gray-700 mb-2">Xóa sản phẩm này?</p>
                      <div className="flex gap-2">
                        <button onClick={() => removeItem(item.id)} className="px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600">Xóa</button>
                        <button onClick={() => setConfirmRemoveId(null)} className="px-3 py-1 bg-gray-200 text-gray-700 text-xs rounded hover:bg-gray-300">Hủy</button>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex justify-between items-center mt-4 pt-4 border-t">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      className="bg-gray-200 hover:bg-gray-300 w-8 h-8 rounded-lg font-bold"
                    >
                      −
                    </button>
                    <span className="text-lg font-medium w-12 text-center">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="bg-gray-200 hover:bg-gray-300 w-8 h-8 rounded-lg font-bold"
                    >
                      +
                    </button>
                  </div>

                  <div className="text-right">
                    <div className="text-sm text-gray-500">Tổng</div>
                    <div className="text-xl font-bold text-blue-600">
                      {formatPrice(item.subtotal)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-4">
              <h3 className="text-xl font-bold mb-4">Tóm Tắt Đơn Hàng</h3>
              
              <div className="space-y-3 mb-4 pb-4 border-b">
                <div className="flex justify-between">
                  <span className="text-gray-600">Số lượng sản phẩm:</span>
                  <span className="font-medium">{cart.total_items}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tạm tính:</span>
                  <span className="font-medium">{formatPrice(cart.total_amount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Phí vận chuyển:</span>
                  <span className="font-medium text-green-600">Miễn phí</span>
                </div>
              </div>

              <div className="flex justify-between items-center mb-6 pb-4 border-b">
                <span className="text-lg font-bold">Tổng cộng:</span>
                <span className="text-2xl font-bold text-blue-600">
                  {formatPrice(cart.total_amount)}
                </span>
              </div>

              <button
                onClick={() => setShowCheckoutForm(true)}
                className="w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-lg font-medium text-lg mb-3"
              >
                🛍️ Tiến Hành Thanh Toán
              </button>

              <button
                onClick={() => navigate('/products')}
                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 py-2 rounded-lg font-medium"
              >
                ← Tiếp tục mua sắm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;
