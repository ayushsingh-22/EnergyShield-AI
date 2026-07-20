import { useState } from 'react'
import { getEntityNeighborhood, queryImpact } from '../api/energyShieldApi'
import GraphView from '../components/graph/GraphView'
import { useEntityName } from '../context/EntityNamesContext'
import { humanize, humanizeLabel } from '../utils/format'

const SUGGESTED_ENTITIES = ['CHK_HORMUZ', 'SUP_IRQ', 'REF_JAM']

// The neighborhood response returns the focus node in `nodes[]` plus edges
// to related ids. Build the node set for the diagram from the returned node
// (keeping its real label) plus every id referenced by an edge; the diagram
// resolves each id's display name through EntityNamesContext, so no label is
// guessed anymore.
function nodesFromNeighborhood(result) {
  if (!result?.edges?.length) return result?.nodes ?? []
  const byId = new Map((result.nodes ?? []).map((node) => [node.entity_id, node]))
  result.edges.forEach((edge) => {
    for (const id of [edge.source_id, edge.target_id]) {
      if (!byId.has(id)) {
        byId.set(id, { entity_id: id, label: 'Entity', properties: {} })
      }
    }
  })
  return Array.from(byId.values())
}

export default function KnowledgeGraphExplorer() {
  const resolveName = useEntityName()
  const [entityId, setEntityId] = useState('CHK_HORMUZ')
  const [neighborhood, setNeighborhood] = useState(null)
  const [impact, setImpact] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function runSearch(id) {
    if (!id.trim()) return
    setLoading(true)
    setError(null)
    try {
      const [neighborhoodResult, impactResult] = await Promise.all([
        getEntityNeighborhood(id.trim()),
        queryImpact(id.trim(), 2),
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

  function handleSearch(event) {
    event.preventDefault()
    runSearch(entityId)
  }

  function handleSuggestionClick(id) {
    setEntityId(id)
    runSearch(id)
  }

  const neighborhoodNodes = nodesFromNeighborhood(neighborhood)

  return (
    <div className="page page-knowledge-graph-explorer">
      <div className="page-header">
        <div>
          <h1>Knowledge Graph Explorer</h1>
          <p className="page-header__copy">
            Supplier → Export Port → Route → Chokepoint → Import Port → Refinery relationships.
          </p>
        </div>
      </div>

      <form className="panel inline-form" onSubmit={handleSearch}>
        <div>
          <label htmlFor="entity-id">Entity ID</label>
          <input
            id="entity-id"
            type="text"
            value={entityId}
            onChange={(event) => setEntityId(event.target.value)}
            placeholder="e.g. CHK_HORMUZ, SUP_IRQ, REF_JAM"
          />
        </div>
        <button type="submit" className="primary-button" disabled={loading}>
          {loading ? 'Searching...' : 'Explore'}
        </button>
        {SUGGESTED_ENTITIES.map((id) => (
          <button
            type="button"
            key={id}
            className="secondary-button"
            onClick={() => handleSuggestionClick(id)}
            disabled={loading}
          >
            {id}
          </button>
        ))}
      </form>
      {error && <p className="error-banner">{error}</p>}

      <section className="card-grid">
        <article className="panel">
          <h2>Direct relationships</h2>
          <p className="panel-copy">{neighborhood?.query_description}</p>
          <GraphView nodes={neighborhoodNodes} edges={neighborhood?.edges ?? []} focusEntityId={entityId} height={280} />
        </article>

        <article className="panel">
          <h2>Downstream impact (2 hops)</h2>
          <p className="panel-copy">{impact?.query_description}</p>
          <GraphView nodes={impact?.nodes ?? []} edges={impact?.edges ?? []} focusEntityId={entityId} height={280} />
        </article>
      </section>

      <section className="card-grid">
        <article className="panel">
          <h2>Direct relationships (table view)</h2>
          <ul className="data-list compact">
            {neighborhood?.edges?.map((edge, index) => (
              <li key={index}>
                <strong>
                  {resolveName(edge.source_id)} -[{humanize(edge.relationship_type)}]-&gt; {resolveName(edge.target_id)}
                </strong>
                <span>
                  {edge.source_id} → {edge.target_id}
                </span>
              </li>
            ))}
            {!neighborhood?.edges?.length && <li>No relationships found.</li>}
          </ul>
        </article>

        <article className="panel">
          <h2>Downstream impact (table view)</h2>
          <ul className="data-list compact">
            {impact?.nodes?.map((node) => (
              <li key={node.entity_id}>
                <strong>{node.properties?.name ?? resolveName(node.entity_id)}</strong>
                <span>{humanizeLabel(node.label)}</span>
                <span>{node.entity_id}</span>
              </li>
            ))}
            {!impact?.nodes?.length && <li>No downstream impact found.</li>}
          </ul>
        </article>
      </section>
    </div>
  )
}
