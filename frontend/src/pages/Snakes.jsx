import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { STATUS } from '../labels'

export default function Snakes() {
  const [snakes, setSnakes] = useState([])
  const [species, setSpecies] = useState([])
  const [form, setForm] = useState({ name: '', species_id: '', birth_date: '', status: 'active' })
  const [error, setError] = useState('')

  const load = () => api('/snakes').then(setSnakes).catch((e) => setError(e.message))

  useEffect(() => {
    load()
    api('/species').then((s) => {
      setSpecies(s)
      if (s.length) setForm((f) => ({ ...f, species_id: String(s[0].id) }))
    })
  }, [])

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  async function add(e) {
    e.preventDefault()
    setError('')
    try {
      await api('/snakes', {
        method: 'POST',
        body: {
          name: form.name,
          species_id: Number(form.species_id),
          birth_date: form.birth_date || null,
          status: form.status,
        },
      })
      setForm({ ...form, name: '', birth_date: '' })
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const speciesName = (id) => species.find((s) => s.id === id)?.name ?? ''

  return (
    <>
      <h1>Moje węże</h1>
      {error && <p className="error">{error}</p>}
      <div className="grid">
        {snakes.map((s) => (
          <Link key={s.id} to={`/snakes/${s.id}`} className="card snake">
            <strong>{s.name}</strong>
            <span>{speciesName(s.species_id)}</span>
            <span className={`badge ${s.status}`}>{STATUS[s.status]}</span>
          </Link>
        ))}
        {snakes.length === 0 && <p className="muted">Nie masz jeszcze węży. Dodaj pierwszego poniżej.</p>}
      </div>

      <form onSubmit={add} className="card">
        <h2>Dodaj węża</h2>
        <label>Imię
          <input value={form.name} onChange={set('name')} required maxLength={80} />
        </label>
        <label>Gatunek
          <select value={form.species_id} onChange={set('species_id')} required>
            {species.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </label>
        <label>Data urodzenia (opcjonalnie)
          <input type="date" value={form.birth_date} onChange={set('birth_date')} />
        </label>
        <label>Status
          <select value={form.status} onChange={set('status')}>
            {Object.entries(STATUS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </label>
        <button type="submit">Dodaj</button>
      </form>
    </>
  )
}