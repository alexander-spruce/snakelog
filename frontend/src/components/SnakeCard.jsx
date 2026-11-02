const fmt = (d) => (d ? new Date(d).toLocaleDateString('pl-PL') : 'nie wiem')

export default function SnakeCard({ card }) {
  const change = card.weight_change_g
  return (
    <div className="card facts">
      <div>
        <span className="muted">Ostatnie ważenie</span>
        <strong>{card.last_weight_g != null ? `${card.last_weight_g} g` : 'nie wiem'}</strong>
        <small>
          {fmt(card.last_weighing_date)}
          {change != null && ` (${change > 0 ? '+' : ''}${change} g)`}
        </small>
      </div>
      <div>
        <span className="muted">Ostatnie karmienie</span>
        <strong>
          {card.last_feeding_date == null ? 'nie wiem' : card.last_feeding_eaten ? 'zjadł' : 'odmówił'}
        </strong>
        <small>{fmt(card.last_feeding_date)}</small>
      </div>
      <div>
        <span className="muted">Ostatnia wylinka</span>
        <strong>{fmt(card.last_shed_date)}</strong>
      </div>
    </div>
  )
}