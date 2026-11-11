import { useEffect, useState } from 'react'
import { BrowserRouter, Link, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { api, getToken, setToken } from './api'
import Alerts from './pages/Alerts'
import Login from './pages/Login'
import Snakes from './pages/Snakes'
import SnakeDetail from './pages/SnakeDetail'

function Layout({ children }) {
  const navigate = useNavigate()
  const location = useLocation()
  const [unread, setUnread] = useState(0)
  const loggedIn = !!getToken()

  useEffect(() => {
    if (!loggedIn) return
    const load = () => api('/alerts/unread-count').then((r) => setUnread(r.count)).catch(() => {})
    load()
    window.addEventListener('alerts-changed', load)
    return () => window.removeEventListener('alerts-changed', load)
  }, [loggedIn, location.pathname])

  if (!loggedIn) return <Navigate to="/login" replace />

  const logout = () => {
    setToken(null)
    navigate('/login')
  }
  return (
    <>
      <header className="top">
        <Link to="/" className="brand">🐍 SnakeLog</Link>
        <nav className="row">
          <Link to="/alerts" className="navlink">
            Alerty{unread > 0 && <span className="count">{unread}</span>}
          </Link>
          <button onClick={logout}>Wyloguj</button>
        </nav>
      </header>
      <main>{children}</main>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Layout><Snakes /></Layout>} />
        <Route path="/snakes/:id" element={<Layout><SnakeDetail /></Layout>} />
        <Route path="/alerts" element={<Layout><Alerts /></Layout>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}