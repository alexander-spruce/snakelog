import { useEffect, useState } from 'react'
import { api } from '../api'
import { REMINDER_TYPE } from '../labels'

export default function RemindersPanel({ snakeId }) {
  const [items, setItems] = useState([])
  const [type, setType] = useState('feeding')
  const [interval, setIntervalDays] = useState(7)
  const [error, setError] = useState('')

  const load = () => api(`/snakes/${snakeId}/reminders`).then(setItems)
  useEffect(() => { load() }, [snakeId])

  async function add(e) {
    e.preventDefault()
    setError('')
    try {
      await api(`/snakes/${snakeId}/reminders`, {
        method: 'POST',
        body: { type, interval_days: Number(interval) },
      })
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const toggle = async (r) => {
    await api(`/snakes/${snakeId}/reminders/${r.id}`, {
      method: 'PATCH',
      body: { status: r.status === 'active' ? 'paused' : 'active' },
    })
    load()
  }

  const remove = async (r) => {
    await api(`/snakes/${snakeId}/reminders/${r.id}`, { method: 'DELETE' })
    load()
  }

  return (
    <div className="card">
      <h2>Przypomnienia e-mail</h2>
      <ul className="list">
        {items.map((r) => (
          <li key={r.id}>
            <strong>{REMINDER_TYPE[r.type]}</strong>
            <span className="grow">
              co {r.interval_days} dni, najbliższy termin: {new Date(r.next_due).toLocaleDateString('pl-PL')}
              {r.status === 'paused' && ' (wstrzymane)'}
            </span>
            <button className="link" onClick={() => toggle(r)}>
              {r.status === 'active' ? 'Wstrzymaj' : 'Wznów'}
            </button>
            <button className="link danger" onClick={() => remove(r)}>Usuń</button>
          </li>
        ))}
        {items.length === 0 && <li className="muted">Brak przypomnień.</li>}
      </ul>
      <form onSubmit={add} className="row">
        <select value={type} onChange={(e) => setType(e.target.value)}>
          {Object.entries(REMINDER_TYPE).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <label className="inline">co
          <input type="number" min="1" max="365" value={interval}
                 onChange={(e) => setIntervalDays(e.target.value)} style={{ width: 70 }} />
          dni
        </label>
        <button type="submit">Dodaj</button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  )
}