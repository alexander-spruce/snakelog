import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function submit(e) {
    e.preventDefault()
    setError('')
    try {
      const r = await api('/auth/forgot-password', { method: 'POST', body: { email } })
      setMessage(r.detail)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="narrow">
      <h1>🐍 SnakeLog</h1>
      <form onSubmit={submit} className="card">
        <h2>Reset hasła</h2>
        <label>E-mail konta
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        {message && <p>{message}</p>}
        {error && <p className="error">{error}</p>}
        <button type="submit">Wyślij link</button>
        <Link to="/login">← Wróć do logowania</Link>
      </form>
    </main>
  )
}