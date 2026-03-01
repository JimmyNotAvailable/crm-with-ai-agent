import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { productsAPI, cartAPI } from '../services/api'
import useNotificationStore from '../stores/notificationStore'
import Pagination from '../components/Pagination'

const PAGE_SIZE = 12

export default function Products() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [addingToCart, setAddingToCart] = useState({})
  const notify = useNotificationStore

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await productsAPI.getAll()
      setProducts(response.data)
    } catch (err) {
      setError('Không thể tải danh sách sản phẩm')
    } finally {
      setLoading(false)
    }
  }

  const addToCart = async (productId) => {
    setAddingToCart({ ...addingToCart, [productId]: true })
    try {
      await cartAPI.addItem(productId, 1)
      notify.getState().success('Đã thêm vào giỏ hàng!')
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể thêm vào giỏ')
    } finally {
      setAddingToCart({ ...addingToCart, [productId]: false })
    }
  }

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.sku.toLowerCase().includes(search.toLowerCase())
  )

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1)
  }, [search])

  const totalPages = Math.ceil(filteredProducts.length / PAGE_SIZE)
  const paginatedProducts = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE
    return filteredProducts.slice(start, start + PAGE_SIZE)
  }, [filteredProducts, currentPage])

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price)
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Đang tải sản phẩm...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded-md">
        {error}
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">📦 Danh Sách Sản Phẩm</h2>
        
        <div className="flex items-center space-x-4">
          <input
            type="text"
            placeholder="Tìm kiếm sản phẩm (tên hoặc SKU)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <div className="text-sm text-gray-600">
            Tìm thấy: <span className="font-bold">{filteredProducts.length}</span> sản phẩm
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {paginatedProducts.map((product) => (
          <div key={product.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6 border border-gray-200">
            <div className="mb-4">
              <div className="flex justify-between items-start mb-2">
                <Link to={`/products/${product.id}`} className="text-lg font-semibold text-gray-800 hover:text-blue-600 transition">
                  {product.name}
                </Link>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  product.stock_quantity > 20 
                    ? 'bg-green-100 text-green-700' 
                    : product.stock_quantity > 0
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-red-100 text-red-700'
                }`}>
                  {product.stock_quantity > 0 ? 'Còn hàng' : 'Hết hàng'}
                </span>
              </div>
              <p className="text-sm text-gray-500 mb-1">SKU: {product.sku}</p>
              {product.category && (
                <span className="inline-block px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded">
                  {product.category}
                </span>
              )}
            </div>

            {product.description && (
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                {product.description}
              </p>
            )}

            <div className="flex justify-between items-center pt-4 border-t border-gray-100">
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {formatPrice(product.price)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Kho: {product.stock_quantity} sản phẩm
                </div>
              </div>
              <button 
                onClick={() => addToCart(product.id)}
                disabled={product.stock_quantity === 0 || addingToCart[product.id]}
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
              >
                {addingToCart[product.id] ? '⏳' : '🛒'} Thêm vào giỏ
              </button>
            </div>
          </div>
        ))}
      </div>

      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        totalItems={filteredProducts.length}
        pageSize={PAGE_SIZE}
        onPageChange={setCurrentPage}
      />

      {filteredProducts.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">Không tìm thấy sản phẩm nào</p>
        </div>
      )}
    </div>
  )
}
