// Shared shimmering placeholder for loading states across pages/panels.
export function SkeletonLine({ width = '100%' }) {
  return <div className="skeleton skeleton-line" style={{ width }} />
}

export function SkeletonCard() {
  return <div className="skeleton skeleton-card" />
}

export function SkeletonList({ rows = 3 }) {
  return (
    <div className="skeleton-list">
      {Array.from({ length: rows }, (_, index) => (
        <SkeletonCard key={index} />
      ))}
    </div>
  )
}
