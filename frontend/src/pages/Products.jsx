import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Products() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('http://localhost:8000/products', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setProducts(response.data)
    } catch (err) {
      setError('Không thể tải danh sách sản phẩm')
    } finally {
      setLoading(false)
    }
  }

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.sku.toLowerCase().includes(search.toLowerCase())
  )

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
        {filteredProducts.map((product) => (
          <div key={product.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6 border border-gray-200">
            <div className="mb-4">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-800">{product.name}</h3>
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
              <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700">
                Xem chi tiết
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">Không tìm thấy sản phẩm nào</p>
        </div>
      )}
    </div>
  )
}
