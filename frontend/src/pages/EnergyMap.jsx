import { useEffect, useState } from 'react'
import { getDigitalTwinExposure, getDigitalTwinMap } from '../api/energyShieldApi'
import SupplyRouteMap from '../components/maps/SupplyRouteMap'

export default function EnergyMap() {
  const [mapData, setMapData] = useState(null)
  const [exposure, setExposure] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([getDigitalTwinMap(), getDigitalTwinExposure()])
      .then(([map, exp]) => {
        if (!cancelled) {
          setMapData(map)
          setExposure(exp)
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="page page-energy-map">
      <div className="page-header">
        <h1>Energy Map</h1>
      </div>
      {error && <p className="error-banner">{error}</p>}

      <section className="panel">
        <SupplyRouteMap mapData={mapData} />
      </section>

      <section className="card-grid">
        <article className="panel">
          <h2>Exposure baseline</h2>
          <ul className="metric-list">
            <li>
              <span>Total supplier exposure</span>
              <strong>{exposure?.total_supplier_exposure_percent ?? 'n/a'}%</strong>
            </li>
            <li>
              <span>Total refineries</span>
              <strong>{exposure?.total_refineries ?? 'n/a'}</strong>
            </li>
            <li>
              <span>Total SPR capacity</span>
              <strong>{exposure?.total_spr_capacity_mmbbl ?? 'n/a'} MMBbl</strong>
            </li>
          </ul>
        </article>
        <article className="panel">
          <h2>Chokepoint exposure</h2>
          <ul className="metric-list">
            {Object.entries(exposure?.chokepoint_exposure_percent ?? {}).map(([id, percent]) => (
              <li key={id}>
                <span>{id}</span>
                <strong>{percent}%</strong>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </div>
  )
}
