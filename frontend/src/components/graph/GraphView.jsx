// Renders a knowledge-graph neighborhood (nodes + edges) as a real node-link
// diagram instead of plain text bullets - Phase 9 section 9.6's
// Supplier -> Port -> Route -> Chokepoint -> Port -> Refinery relationship view.
import { useMemo } from 'react'
import { useEntityName } from '../../context/EntityNamesContext'
import { humanize, humanizeLabel } from '../../utils/format'

// Categorical series validated with the dataviz skill's validate_palette.js
// against this app's surface (#fcfaf6) - see App.css tokens for the same set.
const LABEL_COLORS = {
  SupplierCountry: 'var(--series-1)',
  SupplierCompany: 'var(--series-1)',
  ExportPort: 'var(--series-4)',
  ShippingRoute: 'var(--series-5)',
  Chokepoint: 'var(--series-6)',
  ImportPort: 'var(--series-2)',
  Refinery: 'var(--series-8)',
  StrategicReserveSite: 'var(--series-7)',
  CrudeGrade: 'var(--series-3)',
}
const FALLBACK_COLOR = 'var(--ink-muted)'

function nodeColor(label) {
  return LABEL_COLORS[label] ?? FALLBACK_COLOR
}

function layoutNodes(nodes, width, height) {
  const radius = Math.min(width, height) / 2 - 56
  const center = { x: width / 2, y: height / 2 }
  const count = Math.max(nodes.length, 1)
  return nodes.map((node, index) => {
    const angle = (2 * Math.PI * index) / count - Math.PI / 2
    return {
      ...node,
      x: center.x + radius * Math.cos(angle),
      y: center.y + radius * Math.sin(angle),
    }
  })
}

export default function GraphView({ nodes, edges, focusEntityId, width = 640, height = 360 }) {
  const resolveName = useEntityName()
  const positioned = useMemo(() => layoutNodes(nodes ?? [], width, height), [nodes, width, height])
  const positionById = useMemo(() => new Map(positioned.map((node) => [node.entity_id, node])), [positioned])

  const legendLabels = useMemo(() => {
    const seen = new Set()
    ;(nodes ?? []).forEach((node) => seen.add(node.label))
    return Array.from(seen)
  }, [nodes])

  if (!nodes?.length) {
    return <div className="component component-graph-view component--empty">No graph nodes to display.</div>
  }

  return (
    <div className="component component-graph-view">
      <svg className="graph-view__svg" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Knowledge graph neighborhood">
        <g>
          {(edges ?? []).map((edge, index) => {
            const from = positionById.get(edge.source_id)
            const to = positionById.get(edge.target_id)
            if (!from || !to) return null
            const midX = (from.x + to.x) / 2
            const midY = (from.y + to.y) / 2
            return (
              <g key={`${edge.source_id}-${edge.target_id}-${index}`}>
                <line className="graph-view__edge" x1={from.x} y1={from.y} x2={to.x} y2={to.y} markerEnd="url(#graph-arrow)" />
                <rect x={midX - 34} y={midY - 8} width={68} height={14} fill="var(--surface-sunken)" opacity={0.9} />
                <text className="graph-view__edge-label" x={midX} y={midY + 3} textAnchor="middle">
                  {humanize(edge.relationship_type)}
                </text>
              </g>
            )
          })}
        </g>
        <defs>
          <marker id="graph-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="var(--border-strong)" />
          </marker>
        </defs>
        <g>
          {positioned.map((node) => {
            const isFocus = node.entity_id === focusEntityId
            return (
              <g key={node.entity_id} transform={`translate(${node.x}, ${node.y})`}>
                <circle
                  className="graph-view__node-circle"
                  r={isFocus ? 15 : 11}
                  fill={nodeColor(node.label)}
                  strokeWidth={isFocus ? 3 : 2}
                />
                <text className="graph-view__node-type" y={-18} textAnchor="middle">
                  {humanizeLabel(node.label)}
                </text>
                <text className="graph-view__node-label" y={26} textAnchor="middle">
                  {node.properties?.name ?? resolveName(node.entity_id)}
                </text>
              </g>
            )
          })}
        </g>
      </svg>
      <div className="graph-view__legend">
        {legendLabels.map((label) => (
          <span key={label} className="graph-view__legend-item">
            <span className="graph-view__legend-swatch" style={{ background: nodeColor(label) }} />
            {humanizeLabel(label)}
          </span>
        ))}
      </div>
    </div>
  )
}
