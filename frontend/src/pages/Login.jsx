import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, setToken } from '../api'

export default function Login() {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function submit(e) {
    e.preventDefault()
    setError('')
    try {
      if (mode === 'register') {
        await api('/auth/register', { method: 'POST', body: { email, password } })
      }
      const t = await api('/auth/login', { method: 'POST', form: { username: email, password } })
      setToken(t.access_token)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="narrow">
      <h1>🐍 SnakeLog</h1>
      <p className="muted">Dziennik opieki nad Twoimi wężami.</p>
      <form onSubmit={submit} className="card">
        <h2>{mode === 'login' ? 'Logowanie' : 'Rejestracja'}</h2>
        <label>E-mail
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>Hasło (min. 8 znaków)
          <input type="password" value={password} minLength={8}
                 onChange={(e) => setPassword(e.target.value)} required />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">{mode === 'login' ? 'Zaloguj' : 'Załóż konto'}</button>
        <button type="button" className="link"
                onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>
          {mode === 'login' ? 'Nie masz konta? Zarejestruj się' : 'Masz konto? Zaloguj się'}
        </button>
          {mode === 'login' && <Link to="/forgot-password">Nie pamiętasz hasła?</Link>}
      </form>
    </main>
  )
}