# EnergyShield AI - Demo Script

A 3-5 minute walkthrough built directly on the Phase 12 "Recommended Demo
Flow" (`ENERGYSHIELD_IMPLEMENTATION_PLAN.md`). Each step below is written
as something a presenter can read aloud or closely paraphrase.

## Setup Checklist Before Demoing

- [ ] Run `docker-compose up --build` and confirm `backend`, `frontend`,
      `postgres`, `neo4j`, and `redis` are all healthy (`GET
      /api/v1/health`).
- [ ] Load seed data: suppliers, ports, refineries, SPR sites, chokepoints,
      and routes from `data/seeds/` into Postgres and the graph
      (`backend/graph/seed_graph.py`), and confirm `/api/v1/digital-twin/map`
      returns non-empty layers.
- [ ] Pre-run one scenario (`RED_SEA_SHIPPING_DISRUPTION`) so a completed
      scenario, recommendation, and report already exist as a fallback if
      the live run is slow or a network-dependent step fails during the
      demo.
- [ ] Confirm the seeded Red Sea maritime alert (or equivalent sample
      record) used in Step 3 is present and not already consumed by a
      prior demo run.
- [ ] Open the dashboard in a browser tab and the API docs
      (`/docs`) in a second tab in case a live API call needs to be shown
      directly.

## Demo Flow

### 1. Open the dashboard

"This is the EnergyShield AI command center. At a glance, it shows our
current top energy risks, the latest structured events we've picked up,
any scenarios that have been triggered, and the recommendations currently
active - everything an energy security analyst needs on one screen."

### 2. Show the digital twin map

"This map is our digital twin of India's crude oil import network: the
supplier countries we source from, the shipping routes and chokepoints
they pass through, the Indian import ports, our refineries, and our
strategic petroleum reserve sites. This is the structural backbone
everything else in the platform reasons over."

### 3. Inject or select a seeded Red Sea maritime alert

"Now let's simulate a real-world trigger. I'll select this seeded maritime
alert about a Red Sea shipping incident - the kind of advisory that would
normally come in from UKMTO or a similar maritime security feed."

### 4. Event extraction agent classifies it

"Watch what happens next: our event extraction agent reads the raw alert
text and converts it into a structured risk event, classifying it as a
`RED_SEA_SHIPPING_DISRUPTION` candidate with a severity and confidence
score - not just a headline, but a machine-readable event our pipeline can
act on."

### 5. Knowledge graph links the event to affected entities

"That event doesn't sit in isolation. Our knowledge graph immediately
links it to the Red Sea shipping route, the Bab el-Mandeb chokepoint, the
Suez route, and every Indian refinery that graph-traversal shows is
downstream of that corridor - so we know exactly who is exposed, not just
that something happened."

### 6. Risk score increases for the corridor

"You can see the Red Sea/Suez corridor risk score jump in real time, and
the dashboard shows exactly why - top drivers like the maritime event
severity, source reliability, and India's import exposure through that
corridor, with the underlying evidence event linked."

### 7. Scenario modeller estimates impact

"Because the risk crossed our threshold, the scenario modeller automatically
runs a `RED_SEA_SHIPPING_DISRUPTION` simulation, estimating supply at risk,
expected delay days, freight cost impact, and which refineries are exposed
- every number here comes with its assumptions shown, not hidden inside a
black box."

### 8. Procurement agent ranks alternatives

"With the impact estimated, the procurement agent ranks alternatives for
us automatically - in this case, rerouting via the Cape of Good Hope and
pulling more from suppliers outside the Red Sea corridor - each option
scored on cost, route safety, supplier reliability, delivery time, and
refinery compatibility."

### 9. SPR agent recommends action

"In parallel, the SPR agent looks at how long this disruption is expected
to persist and recommends whether to simply monitor the situation or begin
a controlled strategic reserve drawdown - it's deliberately conservative,
so a short, low-severity event won't trigger reserve releases unnecessarily."

### 10. Dashboard shows the action plan and generates a report

"Finally, everything comes together into a single action plan on the
dashboard, and with one click we generate an executive-ready report
summarizing the event, the risk change, the scenario impact, and the
recommended response - fully backed by an audit trail from the original
signal all the way through to this recommendation."

## Closing Line

"That's the full loop: a real-world signal becomes a structured event,
the knowledge graph tells us who's exposed, risk scores update
automatically, a scenario quantifies the impact, and procurement and
reserve recommendations come out the other end - all explainable and
auditable, and built to extend beyond crude oil into LNG, coal,
fertilizers, and critical minerals."
