import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { ALERT_TYPE } from '../labels'

export default function Alerts() {
  const [items, setItems] = useState([])
  const [onlyUnread, setOnlyUnread] = useState(false)
  const [error, setError] = useState('')

  const load = () =>
    api(`/alerts?unread_only=${onlyUnread}`).then(setItems).catch((e) => setError(e.message))
  useEffect(() => { load() }, [onlyUnread])

  const changed = () => {
    load()
    window.dispatchEvent(new Event('alerts-changed'))
  }
  const markRead = async (id) => {
    await api(`/alerts/${id}/read`, { method: 'PATCH' })
    changed()
  }
  const markAll = async () => {
    await api('/alerts/read-all', { method: 'POST' })
    changed()
  }

  return (
    <>
      <div className="row between">
        <h1>Alerty zdrowotne</h1>
        <div className="row">
          <label className="inline">
            <input type="checkbox" checked={onlyUnread} onChange={(e) => setOnlyUnread(e.target.checked)} />
            tylko nieprzeczytane
          </label>
          <button className="secondary" onClick={markAll}>Oznacz wszystkie jako przeczytane</button>
        </div>
      </div>
      {error && <p className="error">{error}</p>}
      {items.length === 0 && <p className="muted">Brak alertów. Alerty tworzy codziennie worker na podstawie dziennika.</p>}
      {items.map((a) => (
        <div key={a.id} className={`card alert ${a.is_read ? '' : 'unread'}`}>
          <div className="row between">
            <strong>{ALERT_TYPE[a.type] ?? a.type}</strong>
            <span className="muted">{new Date(a.created_at).toLocaleDateString('pl-PL')}</span>
          </div>
          <span>Wąż: <Link to={`/snakes/${a.snake_id}`}>{a.snake_name}</Link></span>
          <p style={{ margin: 0 }}>{a.message}</p>
          {!a.is_read && (
            <div><button className="secondary" onClick={() => markRead(a.id)}>Oznacz jako przeczytany</button></div>
          )}
        </div>
      ))}
      <p className="muted disclaimer">
        Alerty mają charakter pomocniczy i nie zastępują wizyty u lekarza weterynarii.
      </p>
    </>
  )
}