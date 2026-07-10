import ProjectBrand from '../components/layout/ProjectBrand'

export default function Dashboard() {
  return (
    <div className="page page-dashboard">
      <ProjectBrand compact subtitle="Command center" />
      <h1>Dashboard</h1>
      <p>
        TODO(Phase 9): Main command center overview showing current top
        risks, latest events, triggered scenarios, and active
        recommendations.
      </p>
    </div>
  )
}
