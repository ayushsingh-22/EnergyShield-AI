import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { getAnalyst, logout } from '../../auth'
import ProjectBrand from './ProjectBrand'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', end: true, icon: '▦' },
  { to: '/risk', label: 'Risk Monitor', icon: '⚠' },
  { to: '/scenarios', label: 'Scenario Simulator', icon: '◈' },
  { to: '/recommendations', label: 'Recommendations', icon: '✓' },
  { to: '/map', label: 'Energy Map', icon: '◉' },
  { to: '/commodities', label: 'Commodities', icon: '●' },
  { to: '/reports', label: 'Reports', icon: '≡' },
]

export default function AppLayout() {
  const analystName = getAnalyst()
  const navigate = useNavigate()

  function handleSignOut() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-layout">
      <aside className="app-layout__sidebar">
        <ProjectBrand compact subtitle="Analyst console" />
        <nav className="app-layout__nav">
          <span className="app-layout__nav-section">Intelligence</span>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                isActive ? 'app-layout__nav-link app-layout__nav-link--active' : 'app-layout__nav-link'
              }
            >
              <span className="app-layout__nav-icon" aria-hidden="true">
                {item.icon}
              </span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="app-layout__sidebar-footer">
          <NavLink to="/settings" className={({ isActive }) => isActive ? 'app-layout__nav-link app-layout__nav-link--active' : 'app-layout__nav-link'}>
            <span className="app-layout__nav-icon" aria-hidden="true">⚙</span> Settings
          </NavLink>
          <span>{analystName ?? 'Analyst'}</span>
          <button type="button" className="link-button" onClick={handleSignOut}>
            Sign out
          </button>
        </div>
      </aside>
      <main className="app-layout__content">
        <Outlet />
      </main>
    </div>
  )
}
