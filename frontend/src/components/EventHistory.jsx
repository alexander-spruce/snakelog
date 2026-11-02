import { useEffect, useState } from 'react'
import { api } from '../api'
import { EVENT_TYPE, describeEvent } from '../labels'

export default function EventHistory({ snakeId, version, onEdit, onChanged }) {
  const [events, setEvents] = useState([])
  const [type, setType] = useState('')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')

  useEffect(() => {
    const q = new URLSearchParams()
    if (type) q.set('type', type)
    if (from) q.set('date_from', from)
    if (to) q.set('date_to', to)
    api(`/snakes/${snakeId}/events?${q}`).then(setEvents)
  }, [snakeId, version, type, from, to])

  async function remove(id) {
    if (!window.confirm('Usunąć ten wpis?')) return
    await api(`/snakes/${snakeId}/events/${id}`, { method: 'DELETE' })
    onChanged()
  }

  return (
    <div className="card">
      <h2>Historia</h2>
      <div className="row filters">
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="">wszystkie typy</option>
          {Object.entries(EVENT_TYPE).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} title="od" />
        <input type="date" value={to} onChange={(e) => setTo(e.target.value)} title="do" />
      </div>
      {events.length === 0 && <p className="muted">Brak wpisów.</p>}
      <ul className="list">
        {events.map((e) => (
          <li key={e.id}>
            <span className="date">{new Date(e.event_date).toLocaleDateString('pl-PL')}</span>
            <strong>{EVENT_TYPE[e.type]}</strong>
            <span className="grow">{describeEvent(e)}</span>
            <button className="link" onClick={() => onEdit(e)}>Edytuj</button>
            <button className="link danger" onClick={() => remove(e.id)}>Usuń</button>
          </li>
        ))}
      </ul>
    </div>
  )
}