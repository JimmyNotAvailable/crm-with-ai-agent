import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import useAuthStore from './stores/authStore'
import NotificationToast from './components/NotificationToast'
import Login from './pages/Login'
import Register from './pages/Register'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import Cart from './pages/Cart'
import Chat from './pages/Chat'
import Tickets from './pages/Tickets'
import KnowledgeBase from './pages/KnowledgeBase'
import Dashboard from './pages/Dashboard'
import Orders from './pages/Orders'
import Profile from './pages/Profile'
import Admin from './pages/Admin'
import Layout from './components/Layout'

function App() {
  const { token, user, fetchUser, logout } = useAuthStore()

  useEffect(() => {
    // On mount, if we have a token but no user, fetch user info
    if (token && !user) {
      fetchUser()
    }
  }, [token])

  if (!token) {
    return (
      <Router>
        <NotificationToast />
        <Routes>
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Login />} />
        </Routes>
      </Router>
    )
  }

  return (
    <Router>
      <NotificationToast />
      <Layout onLogout={logout}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:id" element={<ProductDetail />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/tickets" element={<Tickets />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/kb" element={<KnowledgeBase />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
