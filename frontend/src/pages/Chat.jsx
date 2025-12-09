import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

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

      const aiMessage = { 
        role: 'assistant', 
        content: response.data.answer,
        tool_used: response.data.tool_used,
        tool_result: response.data.tool_result
      }
      setMessages(prev => [...prev, aiMessage])
      
      if (!conversationId) {
        setConversationId(response.data.conversation_id)
      }
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: '❌ Lỗi: ' + (err.response?.data?.detail || 'Không thể kết nối tới server')
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
    'Chính sách bảo hành là gì?',
    'Laptop nào phù hợp cho văn phòng?',
    'Có khuyến mãi gì trong tháng này?',
    'Tìm điện thoại Samsung giá rẻ',
    'Đơn hàng của tôi thế nào?',
    'Cách đổi trả sản phẩm?'
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-t-lg">
          <h2 className="text-2xl font-bold flex items-center">
            <span className="mr-3">💬</span>
            Chat với AI Assistant
          </h2>
          <p className="text-blue-100 mt-2 text-sm">
            Hỏi bất kỳ điều gì về sản phẩm, chính sách, hoặc dịch vụ của chúng tôi
          </p>
        </div>

        <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-gray-50">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🤖</div>
              <p className="text-gray-600 mb-6">Xin chào! Tôi có thể giúp gì cho bạn?</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-2xl mx-auto">
                {suggestedQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(q)}
                    className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-blue-50 hover:border-blue-300 text-sm text-left transition"
                  >
                    💡 {q}
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
                className={`max-w-[80%] rounded-lg p-4 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                <div className="flex items-start">
                  <span className="mr-2 text-xl">
                    {msg.role === 'user' ? '👤' : '🤖'}
                  </span>
                  <div className="flex-1">
                    <div className="text-xs opacity-70 mb-1">
                      {msg.role === 'user' ? 'Bạn' : 'AI Assistant'}
                    </div>
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </div>
                </div>
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
              placeholder="Nhập câu hỏi của bạn..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              {loading ? '⏳' : '📤'} Gửi
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            💡 Tip: Nhấn Enter để gửi tin nhắn
          </p>
        </div>
      </div>

      {conversationId && (
        <div className="mt-4 text-center text-sm text-gray-600">
          <p>🔗 Conversation ID: <code className="bg-gray-100 px-2 py-1 rounded">{conversationId}</code></p>
          <p className="text-xs text-gray-500 mt-1">Lịch sử chat được lưu tự động</p>
        </div>
      )}
    </div>
  )
}
