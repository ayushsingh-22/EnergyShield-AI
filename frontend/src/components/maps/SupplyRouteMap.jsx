// Renders the geospatial digital twin map with suppliers, routes, chokepoints, ports, refineries, and SPR sites.
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { GeoJSON, MapContainer, TileLayer } from 'react-leaflet'

const ENTITY_COLORS = {
  ExportPort: '#8b5e34',
  ImportPort: '#2f7d4f',
  Refinery: '#c0392b',
  SPR: '#5b3fd6',
  ShippingRoute: '#2b6cb0',
  Chokepoint: '#d05c30',
}

function styleFeature(feature) {
  const color = ENTITY_COLORS[feature?.properties?.entity_type] ?? '#6b6375'
  return { color, weight: feature?.geometry?.type === 'LineString' ? 3 : 2, fillOpacity: 0.35 }
}

function pointToLayer(feature, latlng) {
  return L.circleMarker(latlng, {
    radius: 6,
    color: ENTITY_COLORS[feature?.properties?.entity_type] ?? '#6b6375',
    fillOpacity: 0.8,
  })
}

function onEachFeature(feature, layer) {
  const props = feature.properties ?? {}
  layer.bindPopup(`<strong>${props.name ?? props.entity_id}</strong><br/>${props.entity_type ?? ''}`)
}

export default function SupplyRouteMap({ mapData }) {
  if (!mapData?.features?.length) {
    return <div className="component component-supply-route-map component--empty">No map data available.</div>
  }

  return (
    <div className="component component-supply-route-map">
      <MapContainer center={[20, 55]} zoom={3} scrollWheelZoom={false} style={{ height: '420px', width: '100%' }}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeoJSON data={mapData} style={styleFeature} onEachFeature={onEachFeature} pointToLayer={pointToLayer} />
      </MapContainer>
      <ul className="map-legend">
        {Object.entries(ENTITY_COLORS).map(([label, color]) => (
          <li key={label}>
            <span className="map-legend__swatch" style={{ background: color }} />
            {label}
          </li>
        ))}
      </ul>
    </div>
  )
}
