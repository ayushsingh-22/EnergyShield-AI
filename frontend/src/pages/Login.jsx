import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import logo from '../assets/logo.png'
import { login } from '../auth'

const VALUE_PROPS = [
  { icon: '◈', text: 'Live corridor and supplier risk scoring across global chokepoints' },
  { icon: '⚠', text: 'Real-time disruption signals from maritime, sanctions, and price feeds' },
  { icon: '✓', text: 'Scenario simulation with ranked procurement and SPR recommendations' },
]

export default function Login() {
  const [name, setName] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  function handleSubmit(event) {
    event.preventDefault()
    if (submitting) return
    setSubmitting(true)
    login(name.trim() || 'Analyst')
    navigate(location.state?.from?.pathname ?? '/', { replace: true })
  }

  return (
    <div className="login-screen">
      <section className="login-hero">
        <div className="login-hero__content">
          <img className="login-hero__mark" src={logo} alt="EnergyShield AI" />
          <p className="login-hero__eyebrow">Analyst console</p>
          <h1 className="login-hero__title">
            Energy supply-chain intelligence, <span>before the disruption hits.</span>
          </h1>
          <ul className="login-hero__list">
            {VALUE_PROPS.map((item) => (
              <li key={item.text}>
                <span className="login-hero__list-icon" aria-hidden="true">
                  {item.icon}
                </span>
                {item.text}
              </li>
            ))}
          </ul>
        </div>
        <div className="login-hero__glow" aria-hidden="true" />
      </section>

      <section className="login-panel">
        <div className="login-card">
          <div className="login-card__header">
            <h2>Sign in</h2>
            <p className="login-card__copy">Enter your analyst name to continue to the command center.</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <label htmlFor="analyst-name">Analyst name</label>
            <input
              id="analyst-name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="e.g. J. Analyst"
              autoFocus
              autoComplete="name"
            />
            <button type="submit" className="primary-button login-form__submit" disabled={submitting}>
              {submitting ? 'Signing in...' : 'Enter command center'}
            </button>
          </form>

          <div className="login-card__footer">
            <span className="login-card__badge">
              <span className="status-pill__dot" aria-hidden="true" />
              Secure session
            </span>
            <span>EnergyShield AI</span>
          </div>
        </div>
      </section>
    </div>
  )
}
