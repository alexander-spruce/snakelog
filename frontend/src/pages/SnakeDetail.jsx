import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import EventForm from '../components/EventForm'
import EventHistory from '../components/EventHistory'
import RemindersPanel from '../components/RemindersPanel'
import SnakeCard from '../components/SnakeCard'
import WeightChart from '../components/WeightChart'
import { STATUS } from '../labels'

export default function SnakeDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [card, setCard] = useState(null)
  const [version, setVersion] = useState(0)
  const [editing, setEditing] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api(`/snakes/${id}/card`).then(setCard).catch((e) => setError(e.message))
  }, [id, version])

  const bump = () => {
    setEditing(null)
    setVersion((v) => v + 1)
  }

  async function changeStatus(e) {
    await api(`/snakes/${id}`, { method: 'PATCH', body: { status: e.target.value } })
    bump()
  }

  async function removeSnake() {
    if (!window.confirm('Usunąć węża wraz z całą historią?')) return
    await api(`/snakes/${id}`, { method: 'DELETE' })
    navigate('/')
  }

  if (error) return <p className="error">{error} <Link to="/">Wróć</Link></p>
  if (!card) return <p className="muted">Ładowanie…</p>

  return (
    <>
      <Link to="/">← Wszystkie węże</Link>
      <div className="row between">
        <h1>{card.snake.name}</h1>
        <div className="row">
          <select value={card.snake.status} onChange={changeStatus}>
            {Object.entries(STATUS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <button className="secondary danger" onClick={removeSnake}>Usuń węża</button>
        </div>
      </div>

      <SnakeCard card={card} />
      <WeightChart snakeId={id} version={version} />
      <EventForm key={editing?.id ?? 'new'} snakeId={id} editing={editing} onDone={bump} />
      <EventHistory snakeId={id} version={version} onEdit={setEditing} onChanged={bump} />
      <RemindersPanel snakeId={id} />

      <p className="muted disclaimer">
        SnakeLog ma charakter pomocniczy i nie zastępuje wizyty u lekarza weterynarii.
      </p>
    </>
  )
}