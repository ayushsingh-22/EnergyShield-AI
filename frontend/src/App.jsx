import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import RequireAuth from './components/layout/RequireAuth'
import { EntityNamesProvider } from './context/EntityNamesContext'
import Dashboard from './pages/Dashboard'
import EnergyMap from './pages/EnergyMap'
import Login from './pages/Login'
import RecommendationCenter from './pages/RecommendationCenter'
import Reports from './pages/Reports'
import RiskMonitor from './pages/RiskMonitor'
import ScenarioSimulator from './pages/ScenarioSimulator'
import Settings from './pages/Settings'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          element={
            <RequireAuth>
              <EntityNamesProvider>
                <AppLayout />
              </EntityNamesProvider>
            </RequireAuth>
          }
        >
          <Route path="/" element={<Dashboard />} />
          <Route path="/risk" element={<RiskMonitor />} />
          <Route path="/scenarios" element={<ScenarioSimulator />} />
          <Route path="/recommendations" element={<RecommendationCenter />} />
          <Route path="/map" element={<EnergyMap />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
