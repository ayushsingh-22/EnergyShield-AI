import logo from '../../assets/logo.png'

export default function ProjectBrand({ compact = false, subtitle }) {
  return (
    <div className={compact ? 'project-brand project-brand--compact' : 'project-brand'}>
      <img className="project-brand__mark" src={logo} alt="EnergyShield AI logo" />
      <div className="project-brand__copy">
        <strong className="project-brand__name">EnergyShield AI</strong>
        {subtitle ? <span className="project-brand__subtitle">{subtitle}</span> : null}
      </div>
    </div>
  )
}