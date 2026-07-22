// Generic overlay dialog: backdrop click, Escape key, and a close button all dismiss it.
import { useEffect } from 'react'

export default function Modal({ title, onClose, children }) {
  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-dialog__header">
          <h3>{title}</h3>
          <button type="button" className="modal-dialog__close" onClick={onClose} aria-label="Close">
            &times;
          </button>
        </div>
        <div className="modal-dialog__body">{children}</div>
      </div>
    </div>
  )
}
