/**
 * Product Detail Page
 * Full product view with specs, add-to-cart, and related products
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { productsAPI, cartAPI } from '../services/api'
import useNotificationStore from '../stores/notificationStore'

const formatPrice = (price) =>
  new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price || 0)

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [quantity, setQuantity] = useState(1)
  const [addingToCart, setAddingToCart] = useState(false)
  const notify = useNotificationStore

  useEffect(() => {
    fetchProduct()
  }, [id])

  const fetchProduct = async () => {
    setLoading(true)
    try {
      const response = await productsAPI.getById(id)
      setProduct(response.data)
    } catch {
      notify.getState().error('Không thể tải thông tin sản phẩm')
    } finally {
      setLoading(false)
    }
  }

  const handleAddToCart = async () => {
    setAddingToCart(true)
    try {
      await cartAPI.addItem(product.id, quantity)
      notify.getState().success(`Đã thêm ${quantity} sản phẩm vào giỏ hàng`)
    } catch (err) {
      notify.getState().error(err.response?.data?.detail || 'Không thể thêm vào giỏ hàng')
    } finally {
      setAddingToCart(false)
    }
  }

  // Parse specs from description
  const parseSpecs = (description) => {
    if (!description) return []
    const specs = []
    const patterns = [
      { label: 'CPU', regex: /CPU[:\s]+([^|]+)/i },
      { label: 'RAM', regex: /RAM[:\s]+([^|]+)/i },
      { label: 'Ổ cứng', regex: /(SSD|HDD|Ổ cứng)[:\s]+([^|]+)/i },
      { label: 'Màn hình', regex: /(Màn hình|Display)[:\s]+([^|]+)/i },
      { label: 'Card đồ họa', regex: /(Card đồ họa|VGA|Card)[:\s]+([^|]+)/i },
      { label: 'Pin', regex: /(Pin|Battery)[:\s]+([^|]+)/i },
      { label: 'Trọng lượng', regex: /(Trọng lượng|Weight)[:\s]+([^|]+)/i },
    ]
    for (const { label, regex } of patterns) {
      const match = description.match(regex)
      if (match) {
        specs.push({ label, value: (match[2] || match[1]).trim() })
      }
    }
    return specs
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Đang tải sản phẩm...</p>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="text-center py-12">
        <p className="text-xl text-gray-600">Không tìm thấy sản phẩm</p>
        <button
          onClick={() => navigate('/products')}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          ← Quay lại sản phẩm
        </button>
      </div>
    )
  }

  const discountPercent = product.original_price && product.price
    ? Math.round((1 - product.price / product.original_price) * 100)
    : 0
  const specs = parseSpecs(product.description)

  return (
    <div className="max-w-5xl mx-auto">
      {/* Breadcrumb */}
      <div className="mb-6 text-sm text-gray-500">
        <button onClick={() => navigate('/products')} className="hover:text-blue-600">
          Sản phẩm
        </button>
        <span className="mx-2">/</span>
        <span className="text-gray-800">{product.name}</span>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image */}
          <div className="bg-gray-100 rounded-lg overflow-hidden aspect-square flex items-center justify-center">
            {product.image_url ? (
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-full object-cover"
                onError={(e) => { e.target.style.display = 'none' }}
              />
            ) : (
              <div className="text-gray-400 text-lg">Không có hình ảnh</div>
            )}
            {discountPercent > 0 && (
              <div className="absolute top-4 left-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                -{discountPercent}%
              </div>
            )}
          </div>

          {/* Info */}
          <div>
            {product.category && (
              <span className="inline-block px-3 py-1 bg-blue-50 text-blue-600 text-xs rounded-full mb-3">
                {product.category}
              </span>
            )}

            <h1 className="text-2xl font-bold text-gray-800 mb-4">{product.name}</h1>

            <p className="text-sm text-gray-500 mb-4">SKU: {product.sku}</p>

            {/* Price */}
            <div className="mb-6">
              <div className="text-3xl font-bold text-blue-600">
                {formatPrice(product.price)}
              </div>
              {product.original_price && product.original_price > product.price && (
                <div className="text-lg text-gray-400 line-through mt-1">
                  {formatPrice(product.original_price)}
                </div>
              )}
            </div>

            {/* Stock */}
            <div className="mb-6">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                product.stock_quantity > 20
                  ? 'bg-green-100 text-green-700'
                  : product.stock_quantity > 0
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-red-100 text-red-700'
              }`}>
                {product.stock_quantity > 0
                  ? `Còn ${product.stock_quantity} sản phẩm`
                  : 'Hết hàng'}
              </span>
            </div>

            {/* Quantity + Add to Cart */}
            <div className="flex items-center gap-4 mb-6">
              <div className="flex items-center border border-gray-300 rounded-md">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-3 py-2 text-gray-600 hover:bg-gray-100"
                >
                  −
                </button>
                <span className="px-4 py-2 border-x border-gray-300 min-w-[50px] text-center">
                  {quantity}
                </span>
                <button
                  onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))}
                  className="px-3 py-2 text-gray-600 hover:bg-gray-100"
                >
                  +
                </button>
              </div>

              <button
                onClick={handleAddToCart}
                disabled={product.stock_quantity === 0 || addingToCart}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
              >
                {addingToCart ? 'Đang thêm...' : '🛒 Thêm vào giỏ hàng'}
              </button>
            </div>

            {/* Specs Table */}
            {specs.length > 0 && (
              <div className="border-t pt-6">
                <h3 className="font-semibold text-gray-700 mb-3">Thông số kỹ thuật</h3>
                <div className="space-y-2">
                  {specs.map((spec, idx) => (
                    <div key={idx} className="flex bg-gray-50 rounded p-2">
                      <span className="font-medium text-gray-600 w-32 flex-shrink-0">{spec.label}</span>
                      <span className="text-gray-800">{spec.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Full Description */}
        {product.description && (
          <div className="mt-8 border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-3">Mô tả sản phẩm</h3>
            <p className="text-gray-600 whitespace-pre-wrap leading-relaxed">
              {product.description}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
