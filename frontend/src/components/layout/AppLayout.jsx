import { NavLink, Outlet } from 'react-router-dom'
import ProjectBrand from './ProjectBrand'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/risk', label: 'Risk Monitor' },
  { to: '/scenarios', label: 'Scenario Simulator' },
  { to: '/recommendations', label: 'Recommendations' },
  { to: '/map', label: 'Energy Map' },
  { to: '/graph', label: 'Knowledge Graph' },
  { to: '/learning', label: 'Learning Center' },
  { to: '/reports', label: 'Reports' },
  { to: '/commodities', label: 'Commodities' },
]

export default function AppLayout() {
  return (
    <div className="app-layout">
      <aside className="app-layout__sidebar">
        <ProjectBrand compact subtitle="Analyst console" />
        <nav className="app-layout__nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (isActive ? 'app-layout__nav-link app-layout__nav-link--active' : 'app-layout__nav-link')}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="app-layout__content">
        <Outlet />
      </main>
    </div>
  )
}
