import { useEffect, useState } from 'react'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api'

export default function WeightChart({ snakeId, version }) {
  const [points, setPoints] = useState([])

  useEffect(() => {
    api(`/snakes/${snakeId}/weights`).then(setPoints)
  }, [snakeId, version])

  return (
    <div className="card">
      <h2>Wykres wagi</h2>
      {points.length < 2 ? (
        <p className="muted">Dodaj co najmniej dwa ważenia, żeby zobaczyć trend.</p>
      ) : (
        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer>
            <LineChart data={points} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis unit=" g" domain={['auto', 'auto']} width={70} />
              <Tooltip formatter={(v) => [`${v} g`, 'Waga']} />
              <Line type="monotone" dataKey="weight_g" stroke="#2f7d4f" strokeWidth={2} dot />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}