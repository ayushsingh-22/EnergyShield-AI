import { useState } from 'react'
import { getEntityNeighborhood, queryImpact } from '../api/energyShieldApi'

export default function KnowledgeGraphExplorer() {
  const [entityId, setEntityId] = useState('CHK_HORMUZ')
  const [neighborhood, setNeighborhood] = useState(null)
  const [impact, setImpact] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSearch(event) {
    event.preventDefault()
    if (!entityId.trim()) return
    setLoading(true)
    setError(null)
    try {
      const [neighborhoodResult, impactResult] = await Promise.all([
        getEntityNeighborhood(entityId.trim()),
        queryImpact(entityId.trim(), 2),
      ])
      setNeighborhood(neighborhoodResult)
      setImpact(impactResult)
    } catch (err) {
      setError(err.message)
      setNeighborhood(null)
      setImpact(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page page-knowledge-graph-explorer">
      <div className="page-header">
        <h1>Knowledge Graph Explorer</h1>
      </div>

      <form className="panel inline-form" onSubmit={handleSearch}>
        <label htmlFor="entity-id">Entity ID</label>
        <input
          id="entity-id"
          type="text"
          value={entityId}
          onChange={(event) => setEntityId(event.target.value)}
          placeholder="e.g. CHK_HORMUZ, SUP_IRQ, REF_JAM"
        />
        <button type="submit" className="primary-button" disabled={loading}>
          {loading ? 'Searching...' : 'Explore'}
        </button>
      </form>
      {error && <p className="error-banner">{error}</p>}

      <section className="card-grid">
        <article className="panel">
          <h2>Direct relationships</h2>
          <p className="panel-copy">{neighborhood?.query_description}</p>
          <ul className="data-list compact">
            {neighborhood?.edges?.map((edge, index) => (
              <li key={index}>
                <strong>
                  {edge.source_id} -[{edge.relationship_type}]-&gt; {edge.target_id}
                </strong>
              </li>
            ))}
            {!neighborhood?.edges?.length && <li>No relationships found.</li>}
          </ul>
        </article>

        <article className="panel">
          <h2>Downstream impact (2 hops)</h2>
          <p className="panel-copy">{impact?.query_description}</p>
          <ul className="data-list compact">
            {impact?.nodes?.map((node) => (
              <li key={node.entity_id}>
                <strong>{node.entity_id}</strong>
                <span>{node.label}</span>
                <span>{node.properties?.name ?? ''}</span>
              </li>
            ))}
            {!impact?.nodes?.length && <li>No downstream impact found.</li>}
          </ul>
        </article>
      </section>
    </div>
  )
}
