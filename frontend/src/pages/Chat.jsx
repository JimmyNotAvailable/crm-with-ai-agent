import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ProductCard from '../components/ProductCard'

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleActionClick = async (action) => {
    // Handle action button clicks
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const formData = new FormData()
      formData.append('query', action.label || '')
      formData.append('action_id', action.action_id)
      if (conversationId) {
        formData.append('conversation_id', conversationId)
      }
      formData.append('use_crm_context', 'true')
      
      const response = await axios.post(
        'http://localhost:8000/rag/chat',
        formData,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )
      
      const aiMessage = buildAIMessage(response.data)
      setMessages(prev => [...prev, aiMessage])
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: 'Loi: ' + (err.response?.data?.detail || 'Khong the ket noi toi server')
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const buildAIMessage = (data) => {
    return { 
      role: 'assistant', 
      content: data.answer,
      tool_used: data.tool_used,
      tool_result: data.tool_result,
      products: data.products || [],
      actions: data.actions || []
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      
      // Send as form data
      const formData = new FormData()
      formData.append('query', input)
      formData.append('top_k', '3')
      if (conversationId) {
        formData.append('conversation_id', conversationId)
      }
      formData.append('use_crm_context', 'true')
      
      const response = await axios.post(
        'http://localhost:8000/rag/chat',
        formData,
        {
          headers: { 
            Authorization: `Bearer ${token}`
          }
        }
      )

      const aiMessage = buildAIMessage(response.data)
      setMessages(prev => [...prev, aiMessage])
      
      if (!conversationId) {
        setConversationId(response.data.conversation_id)
      }
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: 'Loi: ' + (err.response?.data?.detail || 'Khong the ket noi toi server')
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const suggestedQuestions = [
    'Chinh sach bao hanh la gi?',
    'Laptop nao phu hop cho van phong?',
    'Co khuyen mai gi trong thang nay?',
    'Tim laptop gaming duoi 25 trieu',
    'So sanh laptop ASUS va MSI',
    'Cach doi tra san pham?'
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-t-lg">
          <h2 className="text-2xl font-bold flex items-center">
            <span className="mr-3">AI</span>
            Chat voi AI Assistant
          </h2>
          <p className="text-blue-100 mt-2 text-sm">
            Hoi bat ky dieu gi ve san pham, chinh sach, hoac dich vu cua chung toi
          </p>
        </div>

        <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-gray-50">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4 text-blue-500 font-bold">AI</div>
              <p className="text-gray-600 mb-6">Xin chao! Toi co the giup gi cho ban?</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-2xl mx-auto">
                {suggestedQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(q)}
                    className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-blue-50 hover:border-blue-300 text-sm text-left transition"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-lg p-4 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                <div className="flex items-start">
                  <span className="mr-2 text-sm font-bold">
                    {msg.role === 'user' ? 'Ban' : 'AI'}
                  </span>
                </div>
                <div className="mt-2 whitespace-pre-wrap">{msg.content}</div>
                
                {/* Display products if available */}
                {msg.products && msg.products.length > 0 && (
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                    {msg.products.slice(0, 4).map((product, pIdx) => (
                      <ProductCard key={pIdx} product={product} compact />
                    ))}
                  </div>
                )}
                
                {/* Display action buttons if available */}
                {msg.actions && msg.actions.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {msg.actions.map((action, aIdx) => (
                      <button
                        key={aIdx}
                        onClick={() => handleActionClick(action)}
                        className="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition"
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-gray-200 p-4 bg-white rounded-b-lg">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Nhap cau hoi cua ban..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              {loading ? '...' : 'Gui'}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Tip: Nhan Enter de gui tin nhan
          </p>
        </div>
      </div>

      {conversationId && (
        <div className="mt-4 text-center text-sm text-gray-600">
          <p>Conversation ID: <code className="bg-gray-100 px-2 py-1 rounded">{conversationId}</code></p>
          <p className="text-xs text-gray-500 mt-1">Lich su chat duoc luu tu dong</p>
        </div>
      )}
    </div>
  )
}
