import { useState, useEffect } from 'react';
import { ticketsAPI } from '../services/api';
import useNotificationStore from '../stores/notificationStore';

const Tickets = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const notify = useNotificationStore;

  // Form state
  const [formData, setFormData] = useState({
    subject: '',
    category: 'GENERAL_INQUIRY',
    initial_message: '',
    order_id: null
  });

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      const response = await ticketsAPI.getAll();
      setTickets(response.data);
    } catch (err) {
      setError('Không thể tải danh sách tickets');
    } finally {
      setLoading(false);
    }
  };

  const fetchTicketDetails = async (ticketId) => {
    try {
      const response = await ticketsAPI.getById(ticketId);
      setSelectedTicket(response.data);
    } catch (err) {
      console.error('Error fetching ticket details:', err);
    }
  };

  const handleCreateTicket = async (e) => {
    e.preventDefault();

    try {
      await ticketsAPI.create(formData);
      notify.getState().success('Đã tạo ticket hỗ trợ thành công');
      setShowCreateForm(false);
      setFormData({
        subject: '',
        category: 'GENERAL_INQUIRY',
        initial_message: '',
        order_id: null
      });
      fetchTickets();
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể tạo ticket');
    }
  };

  const handleAddMessage = async (e) => {
    e.preventDefault();

    try {
      await ticketsAPI.addMessage(selectedTicket.id, newMessage);
      setNewMessage('');
      fetchTicketDetails(selectedTicket.id);
      notify.getState().success('Đã gửi tin nhắn');
    } catch (err) {
      notify.getState().error('Không thể gửi tin nhắn');
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      'OPEN': 'bg-blue-100 text-blue-800',
      'IN_PROGRESS': 'bg-yellow-100 text-yellow-800',
      'WAITING_CUSTOMER': 'bg-purple-100 text-purple-800',
      'RESOLVED': 'bg-green-100 text-green-800',
      'CLOSED': 'bg-gray-100 text-gray-800'
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityBadge = (priority) => {
    const badges = {
      'LOW': 'bg-gray-100 text-gray-600',
      'MEDIUM': 'bg-blue-100 text-blue-600',
      'HIGH': 'bg-orange-100 text-orange-600',
      'URGENT': 'bg-red-100 text-red-600'
    };
    return badges[priority] || 'bg-gray-100 text-gray-600';
  };

  const getCategoryLabel = (category) => {
    const labels = {
      'GENERAL_INQUIRY': 'Yêu cầu chung',
      'ORDER_ISSUE': 'Vấn đề đơn hàng',
      'PRODUCT_QUESTION': 'Câu hỏi sản phẩm',
      'COMPLAINT': 'Khiếu nại',
      'TECHNICAL_SUPPORT': 'Hỗ trợ kỹ thuật',
      'REFUND_REQUEST': 'Yêu cầu hoàn tiền'
    };
    return labels[category] || category;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-gray-600">Đang tải...</div>
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
    <div className="max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">🎫 Hỗ Trợ Khách Hàng</h1>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-medium transition"
        >
          + Tạo Ticket Mới
        </button>
      </div>

      {/* Create Ticket Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Tạo Ticket Hỗ Trợ</h2>
            <form onSubmit={handleCreateTicket}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tiêu đề
                </label>
                <input
                  type="text"
                  required
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Mô tả ngắn gọn vấn đề..."
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Danh mục
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="GENERAL_INQUIRY">Yêu cầu chung</option>
                  <option value="ORDER_ISSUE">Vấn đề đơn hàng</option>
                  <option value="PRODUCT_QUESTION">Câu hỏi sản phẩm</option>
                  <option value="COMPLAINT">Khiếu nại</option>
                  <option value="TECHNICAL_SUPPORT">Hỗ trợ kỹ thuật</option>
                  <option value="REFUND_REQUEST">Yêu cầu hoàn tiền</option>
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mô tả chi tiết
                </label>
                <textarea
                  required
                  value={formData.initial_message}
                  onChange={(e) => setFormData({ ...formData, initial_message: e.target.value })}
                  rows="6"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Mô tả chi tiết vấn đề của bạn..."
                />
              </div>

              <div className="flex gap-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-2 rounded-lg font-medium"
                >
                  Tạo Ticket
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 rounded-lg font-medium"
                >
                  Hủy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Ticket Detail Modal */}
      {selectedTicket && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold">{selectedTicket.subject}</h2>
                <p className="text-gray-500 text-sm">#{selectedTicket.ticket_number}</p>
              </div>
              <button
                onClick={() => setSelectedTicket(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="flex gap-2 mb-6">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(selectedTicket.status)}`}>
                {selectedTicket.status}
              </span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityBadge(selectedTicket.priority)}`}>
                {selectedTicket.priority}
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                {getCategoryLabel(selectedTicket.category)}
              </span>
            </div>

            {/* Messages */}
            <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
              {selectedTicket.messages?.map((msg) => (
                <div
                  key={msg.id}
                  className={`p-4 rounded-lg ${
                    msg.is_staff ? 'bg-blue-50 border-l-4 border-blue-500' : 'bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-medium text-sm">
                      {msg.is_staff ? '🎧 Nhân viên hỗ trợ' : '👤 Bạn'}
                      {msg.is_ai_generated && ' 🤖 (AI)'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(msg.created_at).toLocaleString('vi-VN')}
                    </span>
                  </div>
                  <p className="text-gray-700 whitespace-pre-wrap">{msg.message}</p>
                </div>
              ))}
            </div>

            {/* Add Message Form */}
            <form onSubmit={handleAddMessage} className="border-t pt-4">
              <textarea
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                rows="3"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Nhập tin nhắn của bạn..."
              />
              <div className="flex gap-2 mt-2">
                <button
                  type="submit"
                  disabled={!newMessage.trim()}
                  className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-6 py-2 rounded-lg font-medium"
                >
                  Gửi
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Tickets List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Mã Ticket
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tiêu đề
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Danh mục
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Trạng thái
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ưu tiên
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ngày tạo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Hành động
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {tickets.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                  Chưa có ticket nào. Nhấn "Tạo Ticket Mới" để bắt đầu.
                </td>
              </tr>
            ) : (
              tickets.map((ticket) => (
                <tr key={ticket.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{ticket.ticket_number}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {ticket.subject}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {getCategoryLabel(ticket.category)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(ticket.status)}`}>
                      {ticket.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getPriorityBadge(ticket.priority)}`}>
                      {ticket.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(ticket.created_at).toLocaleDateString('vi-VN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => fetchTicketDetails(ticket.id)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Xem chi tiết
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Tickets;
