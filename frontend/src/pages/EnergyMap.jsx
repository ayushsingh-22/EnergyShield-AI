import { useEffect, useState } from 'react'
import { getDigitalTwinExposure, getDigitalTwinMap } from '../api/energyShieldApi'
import { SkeletonCard, SkeletonList } from '../components/layout/Skeleton'
import SupplyRouteMap from '../components/maps/SupplyRouteMap'

export default function EnergyMap() {
  const [mapData, setMapData] = useState(null)
  const [exposure, setExposure] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

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
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="page page-energy-map">
      <div className="page-header">
        <div>
          <h1>Energy Map</h1>
          <p className="page-header__copy">Suppliers, routes, chokepoints, ports, refineries, and SPR sites.</p>
        </div>
      </div>
      {error && <p className="error-banner">{error}</p>}

      <section className="panel">
        {loading ? <SkeletonCard /> : <SupplyRouteMap mapData={mapData} />}
      </section>

      <section className="card-grid">
        <article className="panel">
          <h2>Exposure baseline</h2>
          {loading ? (
            <SkeletonList rows={3} />
          ) : (
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
          )}
        </article>
        <article className="panel">
          <h2>Chokepoint exposure</h2>
          {loading ? (
            <SkeletonList rows={3} />
          ) : (
            <ul className="metric-list">
              {Object.entries(exposure?.chokepoint_exposure_percent ?? {}).map(([id, percent]) => (
                <li key={id}>
                  <span>{id}</span>
                  <strong>{percent}%</strong>
                </li>
              ))}
              {!Object.keys(exposure?.chokepoint_exposure_percent ?? {}).length && (
                <li>No chokepoint exposure data yet.</li>
              )}
            </ul>
          )}
        </article>
      </section>
    </div>
  )
}
