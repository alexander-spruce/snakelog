import { useState } from 'react'
import { api } from '../api'
import { EVENT_TYPE, OTHER, SHED, today } from '../labels'

const defaultCategory = (type) => (type === 'shed' ? 'complete' : type === 'other' ? 'cleaning' : '')

export default function EventForm({ snakeId, editing, onDone }) {
  const [type, setType] = useState(editing?.type ?? 'weighing')
  const [date, setDate] = useState(editing?.event_date ?? today())
  const [weight, setWeight] = useState(editing?.weight_g ?? '')
  const [food, setFood] = useState(editing?.food_type ?? '')
  const [eaten, setEaten] = useState(editing?.eaten ?? true)
  const [category, setCategory] = useState(editing?.note_category ?? '')
  const [note, setNote] = useState(editing?.note ?? '')
  const [error, setError] = useState('')

  function changeType(t) {
    setType(t)
    setCategory(defaultCategory(t))
  }

  async function submit(e) {
    e.preventDefault()
    setError('')
    const body = { type, event_date: date }
    if (type === 'weighing') body.weight_g = Number(weight)
    if (type === 'feeding') {
      body.food_type = food || null
      body.eaten = eaten
    }
    if (type === 'shed') body.note_category = category || 'complete'
    if (type === 'other') {
      body.note_category = category || 'cleaning'
      body.note = note || null
    }
    try {
      if (editing) {
        await api(`/snakes/${snakeId}/events/${editing.id}`, { method: 'PUT', body })
      } else {
        await api(`/snakes/${snakeId}/events`, { method: 'POST', body })
      }
      onDone()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={submit} className="card">
      <h2>{editing ? 'Edytuj wpis' : 'Nowy wpis w dzienniku'}</h2>
      <label>Typ
        <select value={type} onChange={(e) => changeType(e.target.value)} disabled={!!editing}>
          {Object.entries(EVENT_TYPE).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </label>
      <label>Data
        <input type="date" value={date} max={today()} onChange={(e) => setDate(e.target.value)} required />
      </label>

      {type === 'weighing' && (
        <label>Waga (g)
          <input type="number" step="0.1" min="0.1" value={weight}
                 onChange={(e) => setWeight(e.target.value)} required />
        </label>
      )}
      {type === 'feeding' && (
        <>
          <label>Rodzaj i wielkość pokarmu
            <input value={food} onChange={(e) => setFood(e.target.value)} placeholder="np. mysz M" />
          </label>
          <label>Wynik
            <select value={String(eaten)} onChange={(e) => setEaten(e.target.value === 'true')}>
              <option value="true">zjadł</option>
              <option value="false">odmówił</option>
            </select>
          </label>
        </>
      )}
      {type === 'shed' && (
        <label>Wylinka
          <select value={category || 'complete'} onChange={(e) => setCategory(e.target.value)}>
            {Object.entries(SHED).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </label>
      )}
      {type === 'other' && (
        <>
          <label>Kategoria
            <select value={category || 'cleaning'} onChange={(e) => setCategory(e.target.value)}>
              {Object.entries(OTHER).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </label>
          <label>Notatka
            <input value={note} onChange={(e) => setNote(e.target.value)} />
          </label>
        </>
      )}

      {error && <p className="error">{error}</p>}
      <div className="row">
        <button type="submit">{editing ? 'Zapisz zmiany' : 'Dodaj wpis'}</button>
        {editing && <button type="button" className="secondary" onClick={onDone}>Anuluj</button>}
      </div>
    </form>
  )
}