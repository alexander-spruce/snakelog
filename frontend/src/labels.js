export const today = () => new Date().toLocaleDateString('sv-SE') // RRRR-MM-DD

export const STATUS = { active: 'aktywny', quarantine: 'kwarantanna', rest: 'okres spoczynku' }
export const EVENT_TYPE = { weighing: 'Ważenie', feeding: 'Karmienie', shed: 'Wylinka', other: 'Inne' }
export const SHED = { complete: 'kompletna', incomplete: 'niekompletna' }
export const OTHER = {
  equipment: 'wymiana sprzętu',
  cleaning: 'czyszczenie zbiornika',
  medication: 'podanie leku',
  rest: 'okres spoczynku',
  quarantine: 'kwarantanna',
}
export const REMINDER_TYPE = { feeding: 'Karmienie', weighing: 'Ważenie', cleaning: 'Czyszczenie' }

export function describeEvent(e) {
  if (e.type === 'weighing') return `${e.weight_g} g`
  if (e.type === 'feeding')
    return `${e.food_type || 'pokarm'}: ${e.eaten ? 'zjadł' : 'odmówił'}`
  if (e.type === 'shed') return SHED[e.note_category] ?? ''
  return [OTHER[e.note_category], e.note].filter(Boolean).join(': ')
}

export const ALERT_TYPE = {
  weight_drop: 'Spadek wagi',
  no_growth_young: 'Brak wzrostu u młodego węża',
  feeding_refusal: 'Długa odmowa jedzenia',
}