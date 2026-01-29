/**
 * ProductCard Component
 * Display product information for laptop/PC products in chat and listing views
 */
import PropTypes from 'prop-types'

export default function ProductCard({ product, compact = false, onAddToCart, onCompare }) {
  // Format price to Vietnamese format
  const formatPrice = (price) => {
    if (!price) return 'Lien he'
    return new Intl.NumberFormat('vi-VN').format(price) + ' VND'
  }

  // Calculate discount percentage
  const discountPercent = product.original_price && product.price
    ? Math.round((1 - product.price / product.original_price) * 100)
    : product.discount_percent || 0

  // Extract short specs from description
  const getShortSpecs = (description) => {
    if (!description) return []
    const specs = []
    
    // Try to extract CPU
    const cpuMatch = description.match(/CPU[:\s]+([^|]+)/i)
    if (cpuMatch) specs.push({ label: 'CPU', value: cpuMatch[1].trim().slice(0, 50) })
    
    // Try to extract RAM
    const ramMatch = description.match(/RAM[:\s]+([^|]+)/i)
    if (ramMatch) specs.push({ label: 'RAM', value: ramMatch[1].trim().slice(0, 30) })
    
    // Try to extract Card
    const vgaMatch = description.match(/(Card đồ họa|VGA|Card)[:\s]+([^|]+)/i)
    if (vgaMatch) specs.push({ label: 'VGA', value: vgaMatch[2]?.trim().slice(0, 40) || vgaMatch[1] })
    
    return specs.slice(0, 3)
  }

  if (compact) {
    // Compact view for chat messages
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 hover:shadow-md transition">
        <div className="flex items-start gap-3">
          {product.image_url && (
            <img 
              src={product.image_url} 
              alt={product.name}
              className="w-16 h-16 object-cover rounded"
              onError={(e) => e.target.style.display = 'none'}
            />
          )}
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-sm text-gray-900 line-clamp-2">
              {product.name}
            </h4>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-blue-600 font-bold text-sm">
                {formatPrice(product.price)}
              </span>
              {discountPercent > 0 && (
                <span className="text-xs text-white bg-red-500 px-1.5 py-0.5 rounded">
                  -{discountPercent}%
                </span>
              )}
            </div>
            {product.category && (
              <span className="text-xs text-gray-500">{product.category}</span>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Full view for product listings
  const specs = getShortSpecs(product.description)

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition">
      {/* Image */}
      <div className="relative aspect-video bg-gray-100">
        {product.image_url ? (
          <img 
            src={product.image_url} 
            alt={product.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23f3f4f6" width="100" height="100"/><text x="50" y="55" text-anchor="middle" fill="%239ca3af" font-size="14">No Image</text></svg>'
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            No Image
          </div>
        )}
        
        {/* Discount badge */}
        {discountPercent > 0 && (
          <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded text-sm font-bold">
            -{discountPercent}%
          </div>
        )}
        
        {/* Stock status */}
        {product.in_stock === false && (
          <div className="absolute top-2 right-2 bg-gray-800 text-white px-2 py-1 rounded text-xs">
            Het hang
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Category & Brand */}
        <div className="flex items-center gap-2 mb-2">
          {product.category && (
            <span className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
              {product.category}
            </span>
          )}
          {product.brand && (
            <span className="text-xs text-gray-600">
              {product.brand}
            </span>
          )}
        </div>

        {/* Name */}
        <h3 className="font-medium text-gray-900 line-clamp-2 mb-2 min-h-[48px]">
          {product.name}
        </h3>

        {/* Specs */}
        {specs.length > 0 && (
          <div className="space-y-1 mb-3 text-xs text-gray-600">
            {specs.map((spec, idx) => (
              <div key={idx} className="flex">
                <span className="font-medium w-12">{spec.label}:</span>
                <span className="flex-1 truncate">{spec.value}</span>
              </div>
            ))}
          </div>
        )}

        {/* Price */}
        <div className="flex items-baseline gap-2 mb-3">
          <span className="text-lg font-bold text-blue-600">
            {formatPrice(product.price)}
          </span>
          {product.original_price && product.original_price > product.price && (
            <span className="text-sm text-gray-400 line-through">
              {formatPrice(product.original_price)}
            </span>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          {onAddToCart && (
            <button
              onClick={() => onAddToCart(product)}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition text-sm font-medium"
            >
              Them vao gio
            </button>
          )}
          {onCompare && (
            <button
              onClick={() => onCompare(product)}
              className="bg-gray-100 text-gray-700 py-2 px-3 rounded hover:bg-gray-200 transition text-sm"
            >
              So sanh
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

ProductCard.propTypes = {
  product: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    name: PropTypes.string.isRequired,
    price: PropTypes.number,
    original_price: PropTypes.number,
    discount_percent: PropTypes.number,
    description: PropTypes.string,
    image_url: PropTypes.string,
    category: PropTypes.string,
    brand: PropTypes.string,
    in_stock: PropTypes.bool
  }).isRequired,
  compact: PropTypes.bool,
  onAddToCart: PropTypes.func,
  onCompare: PropTypes.func
}
