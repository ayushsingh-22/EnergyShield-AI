// Fetches the backend's id -> display-name map once (GET /digital-twin/names)
// and exposes a resolver so any component can turn an entity id like
// "CHK_HORMUZ" / "SUP_IRQ" / "REF_JAM" into "Strait of Hormuz" / "Iraq" /
// "Reliance Jamnagar" for display, falling back to the raw id when a name
// isn't known.
import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { getEntityNames } from '../api/energyShieldApi'

const EntityNamesContext = createContext({ names: {}, resolveName: (id) => id })

export function EntityNamesProvider({ children }) {
  const [names, setNames] = useState({})

  useEffect(() => {
    let cancelled = false
    getEntityNames()
      .then((data) => {
        if (!cancelled && data) setNames(data)
      })
      .catch(() => {
        // Name resolution is a display nicety; if it fails, components fall
        // back to raw ids and the app keeps working.
      })
    return () => {
      cancelled = true
    }
  }, [])

  const resolveName = useCallback((entityId) => names[entityId] ?? entityId, [names])

  return <EntityNamesContext.Provider value={{ names, resolveName }}>{children}</EntityNamesContext.Provider>
}

export function useEntityName() {
  return useContext(EntityNamesContext).resolveName
}
