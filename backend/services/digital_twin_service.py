"""Digital Twin Service for managing the entities of the supply chain."""

from __future__ import annotations

import csv
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from models.core_schema import Coordinates
from models.digital_twin_schema import (
    SupplierCountry,
    ExportPort,
    ShippingRoute,
    Chokepoint,
    ImportPort,
    Refinery,
    StrategicReserveSite
)

logger = logging.getLogger(__name__)

# Anchored to this file's location (not the process cwd) so the default
# resolves correctly whether the app is run from the repo root, from
# `backend/` (per README), or in Docker where `data/` is mounted one level
# above the `/app` working directory - all three put `data/seeds` two
# parents above this file.
_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "seeds"


class DigitalTwinService:
    def __init__(self, data_dir: str | Path = _DEFAULT_DATA_DIR):
        self.data_dir = Path(data_dir)
        self.suppliers: Dict[str, SupplierCountry] = {}
        self.export_ports: Dict[str, ExportPort] = {}
        self.import_ports: Dict[str, ImportPort] = {}
        self.refineries: Dict[str, Refinery] = {}
        self.spr_sites: Dict[str, StrategicReserveSite] = {}
        self.routes: Dict[str, ShippingRoute] = {}
        self.chokepoints: Dict[str, Chokepoint] = {}

    def load_seed_data(self):
        """Loads all seed data into in-memory dictionaries."""
        self._load_suppliers()
        self._load_export_ports()
        self._load_import_ports()
        self._load_refineries()
        self._load_spr_sites()
        self._load_routes()
        self._load_chokepoints()
        logger.info("Successfully loaded all Digital Twin seed data.")

    def _load_suppliers(self):
        file_path = self.data_dir / "crude_suppliers.csv"
        if not file_path.exists():
            return
        with open(file_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                supplier = SupplierCountry(
                    entity_id=row["entity_id"],
                    name=row["name"],
                    country=row["country"],
                    region=row["region"],
                    import_share_percent=float(row["import_share_percent"]),
                    default_export_port_id=row.get("default_export_port_id"),
                    default_shipping_route_id=row.get("default_shipping_route_id"),
                    data_source=row.get("data_source", "estimated"),
                    is_simulated=row.get("is_simulated", "false").lower() == "true"
                )
                self.suppliers[supplier.id] = supplier

    def _load_export_ports(self):
        file_path = self.data_dir / "export_ports.csv"
        if not file_path.exists():
            return
        with open(file_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                port = ExportPort(
                    entity_id=row["entity_id"],
                    name=row["name"],
                    country=row["country"],
                    capacity_mmt=float(row["capacity_mmt"]) if row.get("capacity_mmt") else None,
                    coordinates=Coordinates(latitude=float(row["lat"]), longitude=float(row["lon"])) if row.get("lat") and row.get("lon") else None
                )
                self.export_ports[port.id] = port

    def _load_import_ports(self):
        file_path = self.data_dir / "import_ports.csv"
        if not file_path.exists():
            return
        with open(file_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                port = ImportPort(
                    entity_id=row["entity_id"],
                    name=row["name"],
                    state=row["state"],
                    capacity_mmt=float(row["capacity_mmt"]) if row.get("capacity_mmt") else None,
                    coordinates=Coordinates(latitude=float(row["lat"]), longitude=float(row["lon"])) if row.get("lat") and row.get("lon") else None
                )
                self.import_ports[port.id] = port

    def _load_refineries(self):
        file_path = self.data_dir / "refineries.csv"
        if not file_path.exists():
            return
        with open(file_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                refinery = Refinery(
                    entity_id=row["entity_id"],
                    name=row["name"],
                    owner=row["owner"],
                    capacity_bpd=float(row["capacity_bpd"]) if row.get("capacity_bpd") else None,
                    connected_import_port_ids=[row["connected_import_port_ids"]] if row.get("connected_import_port_ids") else [],
                    location_name=row["location_name"],
                    coordinates=Coordinates(latitude=float(row["lat"]), longitude=float(row["lon"])) if row.get("lat") and row.get("lon") else None
                )
                self.refineries[refinery.id] = refinery

    def _load_spr_sites(self):
        file_path = self.data_dir / "spr_sites.csv"
        if not file_path.exists():
            return
        with open(file_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                spr = StrategicReserveSite(
                    entity_id=row["entity_id"],
                    name=row["name"],
                    capacity_mmbbl=float(row["capacity_mmbbl"]) if row.get("capacity_mmbbl") else None,
                    supported_refinery_ids=[row["supported_refinery_ids"]] if row.get("supported_refinery_ids") else [],
                    coordinates=Coordinates(latitude=float(row["lat"]), longitude=float(row["lon"])) if row.get("lat") and row.get("lon") else None
                )
                self.spr_sites[spr.id] = spr

    def _load_routes(self):
        file_path = self.data_dir / "routes.geojson"
        if not file_path.exists():
            return
        with open(file_path, mode='r') as f:
            data = json.load(f)
            for feature in data.get("features", []):
                props = feature.get("properties", {})
                route = ShippingRoute(
                    entity_id=props["entity_id"],
                    name=props["name"],
                    origin_port_id=props["origin_port_id"],
                    destination_port_id=props["destination_port_id"],
                    affected_chokepoint_ids=props.get("affected_chokepoint_ids", []),
                    distance_km=props.get("distance_km"),
                    estimated_transit_days=props.get("estimated_transit_days"),
                    route_status=props.get("route_status", "OPEN"),
                    route_type=props.get("route_type", "MARITIME"),
                    route_geometry=feature.get("geometry")
                )
                self.routes[route.id] = route

    def _load_chokepoints(self):
        file_path = self.data_dir / "chokepoints.geojson"
        if not file_path.exists():
            return
        with open(file_path, mode='r') as f:
            data = json.load(f)
            for feature in data.get("features", []):
                props = feature.get("properties", {})
                chk = Chokepoint(
                    entity_id=props["entity_id"],
                    name=props["name"],
                    country_region=props["country_region"],
                    importance_score=props.get("importance_score", 0.0),
                    geometry=feature.get("geometry")
                )
                self.chokepoints[chk.id] = chk

    def get_suppliers(self) -> List[SupplierCountry]:
        return list(self.suppliers.values())

    def get_routes(self) -> List[ShippingRoute]:
        return list(self.routes.values())

    def get_chokepoints(self) -> List[Chokepoint]:
        return list(self.chokepoints.values())

    def get_import_ports(self) -> List[ImportPort]:
        return list(self.import_ports.values())

    def get_refineries(self) -> List[Refinery]:
        return list(self.refineries.values())

    def get_spr_sites(self) -> List[StrategicReserveSite]:
        return list(self.spr_sites.values())

    def find_supplier(self, entity_id: str) -> Optional[SupplierCountry]:
        return self.suppliers.get(entity_id)

    def find_route(self, entity_id: str) -> Optional[ShippingRoute]:
        return self.routes.get(entity_id)

    def find_refinery(self, entity_id: str) -> Optional[Refinery]:
        return self.refineries.get(entity_id)

    def find_entity(self, entity_id: str) -> Optional[Any]:
        if entity_id in self.suppliers: return self.suppliers[entity_id]
        if entity_id in self.export_ports: return self.export_ports[entity_id]
        if entity_id in self.import_ports: return self.import_ports[entity_id]
        if entity_id in self.refineries: return self.refineries[entity_id]
        if entity_id in self.spr_sites: return self.spr_sites[entity_id]
        if entity_id in self.routes: return self.routes[entity_id]
        if entity_id in self.chokepoints: return self.chokepoints[entity_id]
        return None

    def get_exposure_summary(self) -> Dict[str, Any]:
        """Calculates baseline deterministic exposure metrics."""
        supplier_exposure = sum(s.import_share_percent for s in self.suppliers.values())

        # Route exposure (sum of import shares tied to that route)
        route_exposure = {}
        for sup in self.suppliers.values():
            if sup.default_shipping_route_id:
                route_exposure[sup.default_shipping_route_id] = route_exposure.get(sup.default_shipping_route_id, 0) + sup.import_share_percent

        # Chokepoint exposure
        chk_exposure = {}
        for route_id, share in route_exposure.items():
            route = self.routes.get(route_id)
            if route:
                for chk_id in route.affected_chokepoint_ids:
                    chk_exposure[chk_id] = chk_exposure.get(chk_id, 0) + share
            else:
                logger.warning(
                    "Supplier exposure references route '%s', which is not in the loaded route seed data.",
                    route_id,
                )

        # Data-quality breakdown of the aggregate exposure percentages
        # above, by each supplier's own `data_source` marking (plan Phase 2
        # validation: "exposure percentages are marked as actual,
        # estimated, or simulated").
        exposure_by_data_source: Dict[str, float] = {}
        for sup in self.suppliers.values():
            key = "simulated" if sup.is_simulated else sup.data_source
            exposure_by_data_source[key] = exposure_by_data_source.get(key, 0) + sup.import_share_percent

        return {
            "total_supplier_exposure_percent": supplier_exposure,
            "route_exposure_percent": route_exposure,
            "chokepoint_exposure_percent": chk_exposure,
            "exposure_by_data_source": exposure_by_data_source,
            "total_refineries": len(self.refineries),
            "total_spr_capacity_mmbbl": sum(s.capacity_mmbbl or 0 for s in self.spr_sites.values())
        }
