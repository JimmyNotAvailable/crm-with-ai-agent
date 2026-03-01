import { useState, useEffect } from 'react';
import { kbAPI } from '../services/api';
import useNotificationStore from '../stores/notificationStore';

export default function KnowledgeBase() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [health, setHealth] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const notify = useNotificationStore;

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    category: '',
    tags: '',
    file: null
  });

  useEffect(() => {
    fetchArticles();
    fetchHealth();
  }, []);

  const fetchArticles = async () => {
    try {
      const response = await kbAPI.getAll();
      setArticles(response.data);
    } catch (err) {
      setError('Không thể tải danh sách tài liệu');
    } finally {
      setLoading(false);
    }
  };

  const fetchHealth = async () => {
    try {
      const response = await kbAPI.healthCheck();
      setHealth(response.data);
    } catch (err) {
      console.error('Cannot fetch health:', err);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    const uploadFormData = new FormData();
    uploadFormData.append('file', formData.file);
    uploadFormData.append('title', formData.title);
    if (formData.category) uploadFormData.append('category', formData.category);
    if (formData.tags) uploadFormData.append('tags', formData.tags);

    try {
      await kbAPI.create(uploadFormData);
      
      notify.getState().success('Tải lên thành công!');
      setShowUploadForm(false);
      setFormData({ title: '', category: '', tags: '', file: null });
      fetchArticles();
      fetchHealth();
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể tải lên');
    }
  };

  const handleDelete = async (articleId) => {
    try {
      await kbAPI.delete(articleId);
      notify.getState().success('Đã xóa tài liệu!');
      setConfirmDeleteId(null);
      fetchArticles();
      fetchHealth();
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể xóa');
    }
  };

  const handleReindex = async (articleId) => {
    try {
      await kbAPI.reindex(articleId);
      notify.getState().success('Đã đánh chỉ mục lại!');
      fetchArticles();
      fetchHealth();
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể đánh chỉ mục');
    }
  };

  const toggleActive = async (article) => {
    try {
      await kbAPI.update(article.id, { is_active: !article.is_active });
      fetchArticles();
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể cập nhật');
    }
  };

  const getHealthColor = (status) => {
    if (status === 'HEALTHY') return 'text-green-600 bg-green-100';
    if (status === 'WARNING') return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Đang tải...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">📚 Quản Lý Tri Thức (Knowledge Base)</h2>
          <p className="text-gray-600 mt-1">Quản lý tài liệu và kiểm tra sức khỏe RAG system</p>
        </div>
        <button
          onClick={() => setShowUploadForm(!showUploadForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
        >
          {showUploadForm ? '✕ Đóng' : '📤 Tải lên tài liệu'}
        </button>
      </div>

      {/* RAG Health Status */}
      {health && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-bold mb-4 flex items-center">
            <span className="mr-2">❤️</span>
            RAG System Health
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{health.total_articles}</div>
              <div className="text-sm text-gray-600">Tổng tài liệu</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{health.indexed_articles}</div>
              <div className="text-sm text-gray-600">Đã đánh chỉ mục</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{health.total_chunks}</div>
              <div className="text-sm text-gray-600">Chunks</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">{health.coverage_rate}%</div>
              <div className="text-sm text-gray-600">Coverage</div>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className={`px-4 py-2 rounded-full font-semibold ${getHealthColor(health.health_status)}`}>
              {health.health_status}
            </span>
            {health.issues.length > 0 && (
              <div className="text-sm text-red-600">
                ⚠️ {health.issues.length} vấn đề: {health.issues.join(', ')}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Upload Form */}
      {showUploadForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-bold mb-4">Tải lên tài liệu mới</h3>
          <form onSubmit={handleUpload}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tiêu đề *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Danh mục
                  </label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    placeholder="VD: Chính sách, Hướng dẫn..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags (phân cách bằng dấu phẩy)
                  </label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    placeholder="VD: bảo hành, đổi trả"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  File (TXT, MD) *
                </label>
                <input
                  type="file"
                  onChange={(e) => setFormData({ ...formData, file: e.target.files[0] })}
                  accept=".txt,.md,.pdf,.docx"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
              >
                📤 Tải lên và đánh chỉ mục
              </button>
            </div>
          </form>
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-md mb-6">
          {error}
        </div>
      )}

      {/* Articles List */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tiêu đề</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Danh mục</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">File</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chunks</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thao tác</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {articles.map((article) => (
              <tr key={article.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">{article.title}</div>
                  {article.tags && (
                    <div className="text-xs text-gray-500 mt-1">🏷️ {article.tags}</div>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {article.category || '-'}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {article.filename}
                  <div className="text-xs text-gray-400">
                    {article.file_type} • {(article.file_size / 1024).toFixed(1)} KB
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {article.chunk_count}
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-col space-y-1">
                    <span className={`px-2 py-1 text-xs rounded-full inline-block ${
                      article.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {article.is_active ? '✓ Active' : '✗ Inactive'}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded-full inline-block ${
                      article.is_indexed ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {article.is_indexed ? '✓ Indexed' : '✗ Not Indexed'}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm space-x-2 relative">
                  <button
                    onClick={() => toggleActive(article)}
                    className="text-blue-600 hover:text-blue-800"
                    title={article.is_active ? 'Vô hiệu hóa' : 'Kích hoạt'}
                  >
                    {article.is_active ? '🔵' : '⚪'}
                  </button>
                  <button
                    onClick={() => handleReindex(article.id)}
                    className="text-green-600 hover:text-green-800"
                    title="Đánh chỉ mục lại"
                  >
                    🔄
                  </button>
                  <button
                    onClick={() => setConfirmDeleteId(article.id)}
                    className="text-red-600 hover:text-red-800"
                    title="Xóa"
                  >
                    🗑️
                  </button>
                  {confirmDeleteId === article.id && (
                    <div className="absolute right-6 top-2 bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-10">
                      <p className="text-sm text-gray-700 mb-2">Xóa tài liệu này?</p>
                      <div className="flex gap-2">
                        <button onClick={() => handleDelete(article.id)} className="px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600">Xóa</button>
                        <button onClick={() => setConfirmDeleteId(null)} className="px-3 py-1 bg-gray-200 text-gray-700 text-xs rounded hover:bg-gray-300">Hủy</button>
                      </div>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {articles.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            Chưa có tài liệu nào. Hãy tải lên tài liệu đầu tiên!
          </div>
        )}
      </div>
    </div>
  );
}
