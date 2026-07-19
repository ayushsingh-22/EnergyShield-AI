import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import ProjectBrand from '../components/layout/ProjectBrand'
import { login } from '../auth'

export default function Login() {
  const [name, setName] = useState('')
  const navigate = useNavigate()
  const location = useLocation()

  function handleSubmit(event) {
    event.preventDefault()
    login(name.trim() || 'Analyst')
    navigate(location.state?.from?.pathname ?? '/', { replace: true })
  }

  return (
    <div className="page page-login">
      <ProjectBrand subtitle="Secure analyst access" />
      <h1>Sign in</h1>
      <p className="hero-copy">
        Local demo session only - there is no backend authentication endpoint in the current API
        contract. Enter any analyst name to continue to the command center.
      </p>
      <form className="login-form" onSubmit={handleSubmit}>
        <label htmlFor="analyst-name">Analyst name</label>
        <input
          id="analyst-name"
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="e.g. J. Analyst"
          autoFocus
        />
        <button type="submit" className="primary-button">
          Enter command center
        </button>
      </form>
    </div>
  )
}
