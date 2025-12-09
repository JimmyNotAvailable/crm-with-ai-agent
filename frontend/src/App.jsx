import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Products from './pages/Products'
import Cart from './pages/Cart'
import Chat from './pages/Chat'
import Tickets from './pages/Tickets'
import KnowledgeBase from './pages/KnowledgeBase'
import Dashboard from './pages/Dashboard'
import Layout from './components/Layout'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))

  const handleLogin = (newToken) => {
    localStorage.setItem('token', newToken)
    setToken(newToken)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken(null)
  }

  if (!token) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <Router>
      <Layout onLogout={handleLogout}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/products" element={<Products />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/tickets" element={<Tickets />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/kb" element={<KnowledgeBase />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
