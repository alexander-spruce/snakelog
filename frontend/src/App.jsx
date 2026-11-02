import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { getToken, setToken } from './api'
import Login from './pages/Login'
import Snakes from './pages/Snakes'
import SnakeDetail from './pages/SnakeDetail'

function Layout({ children }) {
  const navigate = useNavigate()
  if (!getToken()) return <Navigate to="/login" replace />
  const logout = () => {
    setToken(null)
    navigate('/login')
  }
  return (
    <>
      <header className="top">
        <Link to="/" className="brand">🐍 SnakeLog</Link>
        <button onClick={logout}>Wyloguj</button>
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
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}