import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api'

export default function ResetPassword() {
  const [params] = useSearchParams()
  const token = params.get('token') ?? ''
  const [password, setPassword] = useState('')
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')

  async function submit(e) {
    e.preventDefault()
    setError('')
    try {
      await api('/auth/reset-password', { method: 'POST', body: { token, new_password: password } })
      setDone(true)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="narrow">
      <h1>🐍 SnakeLog</h1>
      <form onSubmit={submit} className="card">
        <h2>Nowe hasło</h2>
        {done ? (
          <>
            <p>Hasło zmienione.</p>
            <Link to="/login">Przejdź do logowania</Link>
          </>
        ) : (
          <>
            <label>Nowe hasło (min. 8 znaków)
              <input type="password" minLength={8} value={password}
                     onChange={(e) => setPassword(e.target.value)} required />
            </label>
            {error && <p className="error">{error}</p>}
            <button type="submit" disabled={!token}>Ustaw hasło</button>
            {!token && <p className="error">Brak tokenu w linku.</p>}
          </>
        )}
      </form>
    </main>
  )
}