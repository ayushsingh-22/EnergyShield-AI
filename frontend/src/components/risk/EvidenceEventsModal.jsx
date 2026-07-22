// Fetches and renders full detail for a set of evidence event ids inside a Modal.
import { useEffect, useState } from 'react'
import { getEvent } from '../../api/energyShieldApi'
import { humanize } from '../../utils/format'
import Modal from '../layout/Modal'

function formatTimestamp(value) {
  if (!value) return 'n/a'
  return new Date(value).toLocaleString()
}

export default function EvidenceEventsModal({ eventIds, onClose }) {
  const [events, setEvents] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setEvents(null)
    setError(null)
    Promise.allSettled(eventIds.map((eventId) => getEvent(eventId)))
      .then((results) => {
        if (cancelled) return
        const resolved = results
          .map((result, index) => (result.status === 'fulfilled' ? result.value : { event_id: eventIds[index], _missing: true }))
        setEvents(resolved)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [eventIds])

  return (
    <Modal title={`Evidence event${eventIds.length > 1 ? 's' : ''} (${eventIds.length})`} onClose={onClose}>
      {error && <p className="error-banner">{error}</p>}
      {!events && !error && <p className="panel-copy">Loading event detail...</p>}
      {events?.map((event) =>
        event._missing ? (
          <div key={event.event_id} className="evidence-event">
            <p className="panel-copy">
              <strong>{event.event_id}</strong> - detail not available.
            </p>
          </div>
        ) : (
          <div key={event.event_id} className="evidence-event">
            <div className="evidence-event__header">
              <strong>{event.title}</strong>
              <span className="pill">{event.event_id}</span>
            </div>
            <div className="evidence-event__meta">
              <span>
                {humanize(event.event_type)} - severity {event.severity} - confidence{' '}
                {Math.round((event.confidence ?? 0) * 100)}%
              </span>
              <span>
                {event.source_name} ({humanize(event.source_reliability)}) - {formatTimestamp(event.detected_at)}
              </span>
              {event.location_name && <span>Location: {event.location_name}</span>}
            </div>
            <p className="panel-copy">{event.summary}</p>
            {event.affected_entities?.length ? (
              <p className="panel-copy">Affected entities: {event.affected_entities.join(', ')}</p>
            ) : null}
            {event.is_simulated ? <span className="tag tag--simulated">simulated</span> : null}
          </div>
        )
      )}
    </Modal>
  )
}
