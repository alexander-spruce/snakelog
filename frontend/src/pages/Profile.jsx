import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Profile() {
  const [email, setEmail] = useState('')
  const [emailPass, setEmailPass] = useState('')
  const [emailMsg, setEmailMsg] = useState('')
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [passMsg, setPassMsg] = useState('')

  useEffect(() => { api('/auth/me').then((u) => setEmail(u.email)) }, [])

  async function saveEmail(e) {
    e.preventDefault()
    setEmailMsg('')
    try {
      const u = await api('/auth/me', { method: 'PATCH', body: { email, current_password: emailPass } })
      setEmail(u.email)
      setEmailPass('')
      setEmailMsg('Zapisano.')
    } catch (err) {
      setEmailMsg(err.message)
    }
  }

  async function savePassword(e) {
    e.preventDefault()
    setPassMsg('')
    try {
      await api('/auth/change-password', {
        method: 'POST', body: { current_password: current, new_password: next },
      })
      setCurrent('')
      setNext('')
      setPassMsg('Hasło zmienione.')
    } catch (err) {
      setPassMsg(err.message)
    }
  }

  return (
    <>
      <h1>Mój profil</h1>
      <form onSubmit={saveEmail} className="card">
        <h2>Adres e-mail</h2>
        <label>E-mail
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>Obecne hasło (potwierdzenie)
          <input type="password" value={emailPass} onChange={(e) => setEmailPass(e.target.value)} required />
        </label>
        {emailMsg && <p className="muted">{emailMsg}</p>}
        <button type="submit">Zapisz e-mail</button>
      </form>

      <form onSubmit={savePassword} className="card">
        <h2>Zmiana hasła</h2>
        <label>Obecne hasło
          <input type="password" value={current} onChange={(e) => setCurrent(e.target.value)} required />
        </label>
        <label>Nowe hasło (min. 8 znaków)
          <input type="password" minLength={8} value={next} onChange={(e) => setNext(e.target.value)} required />
        </label>
        {passMsg && <p className="muted">{passMsg}</p>}
        <button type="submit">Zmień hasło</button>
      </form>
    </>
  )
}