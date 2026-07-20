"""Digital Twin API routes (Phase 2)."""

from __future__ import annotations

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException

from services.digital_twin_service import DigitalTwinService
from models.digital_twin_schema import (
    SupplierCountry,
    ShippingRoute,
    Chokepoint,
    ImportPort,
    Refinery,
    StrategicReserveSite
)

router = APIRouter(prefix="/api/v1/digital-twin", tags=["digital-twin"])

# Initialize and load data on startup
service = DigitalTwinService()
service.load_seed_data()

@router.get("/map")
def get_digital_twin_map():
    """Returns a frontend-ready GeoJSON FeatureCollection of all spatial entities."""
    features = []
    
    # Export Ports
    for port in service.export_ports.values():
        if port.coordinates:
            features.append({
                "type": "Feature",
                "properties": {
                    "entity_id": port.id,
                    "name": port.name,
                    "entity_type": "ExportPort",
                    "style_hints": {"color": "blue"}
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [port.coordinates.longitude, port.coordinates.latitude]
                }
            })
            
    # Import Ports
    for port in service.import_ports.values():
        if port.coordinates:
            features.append({
                "type": "Feature",
                "properties": {
                    "entity_id": port.id,
                    "name": port.name,
                    "entity_type": "ImportPort",
                    "style_hints": {"color": "green"}
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [port.coordinates.longitude, port.coordinates.latitude]
                }
            })
            
    # Refineries
    for ref in service.refineries.values():
        if ref.coordinates:
            features.append({
                "type": "Feature",
                "properties": {
                    "entity_id": ref.id,
                    "name": ref.name,
                    "entity_type": "Refinery",
                    "style_hints": {"color": "orange"}
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [ref.coordinates.longitude, ref.coordinates.latitude]
                }
            })
            
    # SPR
    for spr in service.spr_sites.values():
        if spr.coordinates:
            features.append({
                "type": "Feature",
                "properties": {
                    "entity_id": spr.id,
                    "name": spr.name,
                    "entity_type": "SPR",
                    "style_hints": {"color": "purple"}
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [spr.coordinates.longitude, spr.coordinates.latitude]
                }
            })

    # Routes
    for route in service.routes.values():
        if route.route_geometry:
            features.append({
                "type": "Feature",
                "properties": {
                    "entity_id": route.id,
                    "name": route.name,
                    "entity_type": "ShippingRoute",
                    "style_hints": {"color": "gray"}
                },
                "geometry": route.route_geometry
            })
            
    # Chokepoints
    for chk in service.chokepoints.values():
        if chk.geometry:
            features.append({
                "type": "Feature",
                "properties": {
                    "entity_id": chk.id,
                    "name": chk.name,
                    "entity_type": "Chokepoint",
                    "style_hints": {"color": "red"}
                },
                "geometry": chk.geometry
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/suppliers", response_model=List[SupplierCountry])
def get_suppliers():
    return service.get_suppliers()

@router.get("/routes", response_model=List[ShippingRoute])
def get_routes():
    return service.get_routes()

@router.get("/chokepoints", response_model=List[Chokepoint])
def get_chokepoints():
    return service.get_chokepoints()

@router.get("/import-ports", response_model=List[ImportPort])
def get_import_ports():
    return service.get_import_ports()

@router.get("/refineries", response_model=List[Refinery])
def get_refineries():
    return service.get_refineries()

@router.get("/spr", response_model=List[StrategicReserveSite])
def get_spr_sites():
    return service.get_spr_sites()

@router.get("/names")
def get_entity_names() -> Dict[str, str]:
    """Flat `{entity_id: display_name}` map across every entity type
    (suppliers, ports, routes, chokepoints, refineries, SPR sites).

    Lets the frontend render human-readable names anywhere it otherwise
    only has an entity id (e.g. risk cards keyed by `CHK_HORMUZ`, affected
    refineries keyed by `REF_JAM`) without changing any existing response
    schema. Covers suppliers too, which `/map` omits because they have no
    geometry."""
    names: Dict[str, str] = {}
    for collection in (
        service.suppliers,
        service.export_ports,
        service.import_ports,
        service.refineries,
        service.spr_sites,
        service.routes,
        service.chokepoints,
    ):
        for entity_id, entity in collection.items():
            names[entity_id] = getattr(entity, "name", entity_id)
    return names


@router.get("/exposure")
def get_exposure():
    return service.get_exposure_summary()

@router.get("/entity/{entity_id}")
def get_entity(entity_id: str):
    entity = service.find_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity
