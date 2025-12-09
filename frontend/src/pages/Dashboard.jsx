import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [kpi, setKpi] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem('token');
    try {
      const [statsRes, kpiRes, anomaliesRes] = await Promise.all([
        axios.get(`${API_URL}/analytics/dashboard?days=30`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/analytics/kpi/overview`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/analytics/anomalies/detect`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      setStats(statsRes.data);
      setKpi(kpiRes.data);
      setAnomalies(anomaliesRes.data);
    } catch (err) {
      setError('Không thể tải dữ liệu dashboard. Vui lòng đăng nhập với tài khoản STAFF/ADMIN.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  const getSeverityColor = (severity) => {
    if (severity === 'HIGH') return 'bg-red-100 text-red-800 border-red-300';
    if (severity === 'MEDIUM') return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-blue-100 text-blue-800 border-blue-300';
  };

  const getHealthColor = (health) => {
    if (health === 'HEALTHY') return 'text-green-600';
    if (health === 'WARNING') return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Đang tải dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-6 rounded-md">
        <p className="font-bold">❌ Lỗi</p>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">📊 Dashboard & KPI</h2>
        <p className="text-gray-600 mt-1">Giám sát hiệu suất kinh doanh và phát hiện bất thường</p>
      </div>

      {/* System Health Alert */}
      {anomalies && anomalies.total_anomalies > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 border-l-4 border-red-500">
          <h3 className="text-lg font-bold text-red-600 mb-4">
            ⚠️ Phát hiện {anomalies.total_anomalies} bất thường - 
            <span className={`ml-2 ${getHealthColor(anomalies.system_health)}`}>
              {anomalies.system_health}
            </span>
          </h3>
          <div className="space-y-3">
            {anomalies.anomalies.map((anomaly, idx) => (
              <div key={idx} className={`p-4 rounded-md border ${getSeverityColor(anomaly.severity)}`}>
                <div className="font-semibold">{anomaly.type}</div>
                <div className="text-sm mt-1">{anomaly.message}</div>
                <div className="text-xs mt-2 italic">💡 {anomaly.recommendation}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* KPI Overview */}
      {kpi && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {/* Revenue */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">Doanh thu (30 ngày)</h3>
              <span className={`text-2xl ${kpi.revenue.trend === 'UP' ? 'text-green-600' : 'text-red-600'}`}>
                {kpi.revenue.trend === 'UP' ? '📈' : '📉'}
              </span>
            </div>
            <div className="text-2xl font-bold text-gray-800">
              {formatCurrency(kpi.revenue.last_30_days)}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              7 ngày: {formatCurrency(kpi.revenue.last_7_days)}
            </div>
          </div>

          {/* Orders */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">Đơn hàng</h3>
              <span className="text-2xl">📦</span>
            </div>
            <div className="text-2xl font-bold text-gray-800">
              {kpi.orders.last_30_days}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Trung bình: {kpi.orders.avg_per_day}/ngày
            </div>
          </div>

          {/* Support */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">Hỗ trợ</h3>
              <span className="text-2xl">🎫</span>
            </div>
            <div className="text-2xl font-bold text-gray-800">
              {kpi.support.ticket_backlog}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              SLA: {kpi.support.sla_compliance}% | Avg: {kpi.support.avg_response_time_hours}h
            </div>
          </div>

          {/* Customer Satisfaction */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">CSAT</h3>
              <span className="text-2xl">⭐</span>
            </div>
            <div className="text-2xl font-bold text-gray-800">
              {kpi.customer_satisfaction.csat_score}/5
            </div>
            <div className="text-xs text-gray-500 mt-2">
              NPS: {kpi.customer_satisfaction.nps}
            </div>
          </div>
        </div>
      )}

      {/* Detailed Stats */}
      {stats && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Orders Stats */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center">
              <span className="mr-2">📦</span>
              Thống kê đơn hàng ({stats.period_days} ngày)
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Tổng đơn hàng:</span>
                <span className="font-bold text-blue-600">{stats.orders.total}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Đơn gần đây:</span>
                <span className="font-bold text-green-600">{stats.orders.recent}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Đang chờ:</span>
                <span className="font-bold text-orange-600">{stats.orders.pending}</span>
              </div>
              <div className="border-t pt-3 flex justify-between items-center">
                <span className="text-gray-600">Doanh thu:</span>
                <span className="font-bold text-purple-600">
                  {formatCurrency(stats.orders.total_revenue)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Giá trị TB/đơn:</span>
                <span className="font-bold text-indigo-600">
                  {formatCurrency(stats.orders.average_order_value)}
                </span>
              </div>
            </div>
          </div>

          {/* Tickets Stats */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center">
              <span className="mr-2">🎫</span>
              Thống kê Tickets
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Tổng tickets:</span>
                <span className="font-bold text-blue-600">{stats.tickets.total}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Đang mở:</span>
                <span className="font-bold text-yellow-600">{stats.tickets.open}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Đang xử lý:</span>
                <span className="font-bold text-blue-600">{stats.tickets.in_progress}</span>
              </div>
              <div className="flex justify-between items-center border-t pt-3">
                <span className="text-gray-600">Cảm xúc tiêu cực:</span>
                <span className="font-bold text-red-600">{stats.tickets.negative_sentiment}</span>
              </div>
            </div>
          </div>

          {/* Products & Customers */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center">
              <span className="mr-2">📦</span>
              Sản phẩm
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Đang bán:</span>
                <span className="font-bold text-green-600">{stats.products.total_active}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Sắp hết hàng:</span>
                <span className="font-bold text-red-600">{stats.products.low_stock}</span>
              </div>
            </div>
          </div>

          {/* Customer Stats */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center">
              <span className="mr-2">👥</span>
              Khách hàng & Tương tác
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Tổng khách hàng:</span>
                <span className="font-bold text-blue-600">{stats.customers.total}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Mới ({stats.period_days} ngày):</span>
                <span className="font-bold text-green-600">{stats.customers.new}</span>
              </div>
              <div className="flex justify-between items-center border-t pt-3">
                <span className="text-gray-600">Hội thoại AI:</span>
                <span className="font-bold text-purple-600">{stats.engagement.conversations}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 text-center text-sm text-gray-500">
        <p>📊 Dashboard cập nhật real-time | 🔄 Refresh để xem dữ liệu mới nhất</p>
      </div>
    </div>
  );
}
