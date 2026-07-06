import { useEffect, useState } from 'react'
import { getHealth } from './api/energyShieldApi'
import './App.css'

// Placeholder shell for Phase 0. Real pages/routing land in Phase 9
// (see frontend/src/pages/ and ENERGYSHIELD_IMPLEMENTATION_PLAN.md).
const PLANNED_PAGES = [
  'Dashboard',
  'Energy Map',
  'Risk Monitor',
  'Scenario Simulator',
  'Recommendation Center',
  'Knowledge Graph Explorer',
  'Learning Center',
  'Commodity Command Center',
  'Reports',
]

function App() {
  const [health, setHealth] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getHealth().then(setHealth).catch((err) => setError(err.message))
  }, [])

  return (
    <section id="center">
      <div>
        <h1>EnergyShield AI</h1>
        <p>AI-driven energy supply chain resilience platform.</p>
        <p>
          Backend status:{' '}
          {error ? `error - ${error}` : health ? health.status : 'checking...'}
        </p>
      </div>
      <div>
        <h2>Planned pages (Phase 9)</h2>
        <ul>
          {PLANNED_PAGES.map((page) => (
            <li key={page}>{page}</li>
          ))}
        </ul>
      </div>
    </section>
  )
}

export default App
