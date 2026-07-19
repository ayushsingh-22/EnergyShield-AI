# EnergyShield AI - Multi-Commodity Roadmap

Summary of Phase 14 (`ENERGYSHIELD_IMPLEMENTATION_PLAN.md`). The platform
starts as a crude-oil MVP but the data model, ingestion, knowledge graph,
risk scoring, scenario modelling, and recommendation layers are
commodity-agnostic by design (Planning Principle #2 and #8) so later
commodities are added as adapters, not new codebases.

## Current Status

All five `CommodityAdapter` implementations exist. `CRUDE_OIL` wraps the
real Phase 2-7 digital twin/risk/scenario data; `LNG`, `COAL`,
`FERTILIZER`, and `CRITICAL_MINERALS` ship a small illustrative
supply-chain entity set (every entity marked `is_simulated: true`) since
live ingestion for those commodities is not built yet - see
`data/seeds/commodity_definitions.yaml` for the same status flags in
machine-readable form. All four non-crude commodities already have at
least one scenario template (`backend/scenarios/templates/`), satisfying
the Phase 14 validation checklist item independent of when their live
ingestion lands.

## The `CommodityAdapter` Interface

`backend/commodities/base_adapter.py` defines one abstract interface that
every commodity must implement so the rest of the platform (ingestion,
graph, risk engine, scenario engine, recommendation agents, frontend) can
stay generic:

```python
from abc import ABC, abstractmethod
from typing import Any

class CommodityAdapter(ABC):
    commodity_type: str

    @abstractmethod
    def get_supply_chain_entities(self) -> list[dict[str, Any]]:
        """Return suppliers, routes, ports, processing sites, demand nodes."""
        raise NotImplementedError

    @abstractmethod
    def get_risk_features(self, signals: list[dict[str, Any]]) -> dict[str, float]:
        """Convert normalized signals into commodity-specific risk features."""
        raise NotImplementedError

    @abstractmethod
    def get_scenario_templates(self) -> list[str]:
        """Return scenario template IDs supported by this commodity."""
        raise NotImplementedError

    @abstractmethod
    def get_recommendation_constraints(self) -> dict[str, Any]:
        """Return procurement, storage, transport, quality, and substitution constraints."""
        raise NotImplementedError
```

The risk engine, scenario engine, and recommendation agents call these four
methods rather than branching on commodity type internally. Adding a
commodity means writing a new adapter class plus scenario template YAML
files - it should not require touching `backend/risk/`,
`backend/scenarios/scenario_engine.py`, or the frontend routing structure.

## Rollout Order

| Order | Commodity | Adapter | Status |
| --- | --- | --- | --- |
| 1 | Crude oil | `crude_oil_adapter.py` | Implemented (MVP, real data) |
| 2 | LNG | `lng_adapter.py` | Implemented (illustrative entities) |
| 3 | Coal | `coal_adapter.py` | Implemented (illustrative entities) |
| 4 | Fertilizer | `fertilizer_adapter.py` | Implemented (illustrative entities) |
| 5 | Critical minerals | `critical_minerals_adapter.py` | Implemented (illustrative entities) |

Rollout was sequential and gated: Phase 14 validation required the crude-oil
MVP to keep working after the adapter abstraction was introduced, and at
least one non-crude commodity to load entities and risk cards before the
next was started, to avoid the risk-register concern that "multi-commodity
expansion breaks crude MVP." `backend/tests/commodities/test_adapters.py`
parametrizes the same shape checks across all five adapters.

Bringing a commodity from "illustrative entities" to "live ingestion" means
replacing that adapter's hardcoded entity list with real collectors/seed
data - the adapter interface itself does not change.

## Commodity-by-Commodity Plan

### LNG

**Why it matters**: Feeds power generation, city gas distribution, and
fertilizer production; import dependence is rising as domestic gas output
plateaus.

**Key entities**: LNG supplier country, liquefaction/export terminal, LNG
vessel route, chokepoint, regasification terminal, demand sector (power,
city gas, fertilizer).

**Scenario templates**: LNG export terminal outage, LNG spot price spike,
regas terminal congestion, shipping route disruption
(`backend/scenarios/templates/lng_supply_shock.yaml`).

### Coal

**Why it matters**: Still the dominant fuel for Indian power generation and
a core industrial feedstock (steel, cement).

**Key entities**: Coal supplier country, export port, shipping route,
Indian import port, rail corridor, power plant/industrial demand node, coal
grade/quality.

**Scenario templates**: Coal port disruption, export restriction, weather
disruption, rail bottleneck
(`backend/scenarios/templates/coal_import_disruption.yaml`).

### Fertilizer

**Why it matters**: Direct link to food security; India imports urea, DAP,
and MOP and is exposed to natural-gas feedstock costs even for
domestically produced urea.

**Key entities**: Fertilizer type (urea, DAP, MOP, ammonia), feedstock
(natural gas, ammonia, phosphates, potash), supplier country, export port,
Indian import port, domestic distribution node, agricultural demand
season.

**Scenario templates**: Natural gas feedstock shock, urea import
disruption, potash export restriction, seasonal demand surge
(`backend/scenarios/templates/fertilizer_feedstock_shock.yaml`).

### Critical Minerals

**Why it matters**: Inputs to EVs, batteries, electronics, and defense
manufacturing; India has very limited domestic reserves and near-total
processing dependence on a small number of countries.

**Key entities**: Mineral (lithium, cobalt, nickel, graphite, rare
earths), mining country, processing country, export port, manufacturing
demand node, dependency sector (EV, battery, electronics, defense).

**Scenario templates**: Export restriction, processing bottleneck,
supplier concentration risk, sanctions/geopolitical escalation
(`backend/scenarios/templates/critical_mineral_export_restriction.yaml`).

## Cross-Commodity Cascade Engine (Phase 14.7, lower priority)

A cascade layer models how a shock in one commodity propagates into
another. Per the Phase 14 validation checklist ("Cross-commodity cascade
logic is documented, even if initially heuristic"), this is a heuristic
cross-reference table today, not a simulation - no code computes these
multipliers yet; a future `backend/scenarios/cascade_engine.py` would read
this same table.

| Source shock | Affected commodity | Heuristic impact |
| --- | --- | --- |
| LNG spot price spike | Fertilizer | Natural-gas feedstock cost rises roughly in proportion to the LNG price move; urea production cost pressure follows within the same quarter |
| Coal import disruption | Crude oil / all commodities | Power-sector stress increases refinery/processing electricity cost and can accelerate diesel genset demand |
| Critical mineral export restriction | Crude oil (indirect) | Slower EV manufacturing keeps oil-linked transport-fuel demand elevated for longer than it otherwise would be |
| Crude oil disruption (chokepoint closure) | LNG, coal, fertilizer | Shared tanker/freight market tightens, raising shipping cost and delay estimates across every other commodity's routes |
| Fertilizer feedstock shock | Crude oil (indirect) | Higher ammonia/urea cost pressures agricultural input costs, an indirect food-security signal rather than a direct energy one |

Applying a row today means manually adjusting a downstream scenario's
`manual_overrides` (e.g. bump `freight_cost_increase_percent` for a coal
scenario after a crude chokepoint closure) rather than an automatic
trigger - the automatic version is future work once at least one cascade
row has been validated against a real historical case in
`backend/learning/disruption_case_library.py`.

## Frontend and API Surface

`frontend/src/pages/CommodityCommandCenter.jsx` and
`frontend/src/components/commodities/CommoditySelector.jsx` let a user
switch commodity without changing the route structure - the same map, risk
card, scenario, and recommendation components render against whichever
commodity's adapter output is loaded. Backed by:

```text
GET  /api/v1/commodities
GET  /api/v1/commodities/{commodity_type}/entities
GET  /api/v1/commodities/{commodity_type}/risk
GET  /api/v1/commodities/{commodity_type}/scenarios
POST /api/v1/commodities/{commodity_type}/scenarios/run
GET  /api/v1/commodities/{commodity_type}/recommendations/{scenario_id}
```
