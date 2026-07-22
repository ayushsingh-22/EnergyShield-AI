# EnergyShield AI - Demo Script

Narration script synced to `Video Project 2.mp4` (repo root, 3:20 / 200s),
a screen-recorded live walkthrough of the running app. Read this aloud
while the recording plays, or use it as narration for a fresh live demo
in the same click order - the timestamps below are targets, not hard cuts.

Each scene opens by naming the exact capability ET AI Hackathon 2026
Problem Statement 2 ("AI-Driven Energy Supply Chain Resilience for
Import-Dependent Economies") asks for, so the mapping to the judging
rubric is explicit throughout.

## Setup Checklist Before Recording/Presenting

- [ ] Run `docker-compose up --build` (or the frontend alone with
      `VITE_USE_MOCK_DATA=true`) and confirm the app is reachable.
- [ ] Confirm seed data loaded: suppliers, ports, refineries, SPR sites,
      chokepoints, and routes from `data/seeds/`.
- [ ] Sign in as an analyst on the login screen.
- [ ] Have the `RED_SEA_SHIPPING_DISRUPTION` scenario template ready to
      select in the Scenario Simulator.
- [ ] Know the scenario ID format (`SCN-YYYYMMDD-000N`) so you can carry it
      from Scenario Simulator -> Recommendations -> Reports on screen.

## Demo Flow

### [0:00-0:18] Scene 1 - Login Screen

[On screen: "Energy supply-chain intelligence, before the disruption
hits."]

"Hackathon Problem Statement 2 asks for AI-driven energy supply chain
resilience for import-dependent economies. Here's the context: India
imports 88% of its crude oil, and 40 to 45% of that transits the Strait of
Hormuz. The 2025 US-Iran standoff sent Brent crude up over 8% in a single
session. Our Strategic Petroleum Reserve covers just 9.5 days of
consumption. And McKinsey found that economies without automated rerouting
took 47 days longer to stabilize supply after a shock. This is EnergyShield
AI - we built the intelligence layer the problem statement says doesn't
exist yet."

### [0:18-0:48] Scene 2 - Command Center / Dashboard

[On screen: Highest Risk Level "Severe", Active Events "5", Top Risks,
Latest Events feed.]

"This is the analyst's Command Center - the Geopolitical Risk Intelligence
Agent the brief calls for, live. Right now: Severe risk across 14 corridors
and suppliers, 5 active events just detected. Novorossiysk to Jamnagar and
Bab el-Mandeb are both scoring Severe. On the right, structured events
pulled continuously from maritime alerts, PortWatch chokepoint data,
sanctions registries, and commodity prices - not a weekly report, a live
feed, exactly as the problem statement demands."

### [0:48-1:23] Scene 3 - Risk Monitor + Evidence + Explainability

[On screen: corridor cards -> evidence modal -> score history /
explainability panel.]

"The Risk Monitor breaks this down per corridor. Strait of Hormuz: Severe,
62.9. Bab el-Mandeb: 65.2."

[Click an "evidence event(s)" link.]

"Every score is backed by evidence - a UKMTO maritime attack warning, an
AIS stream showing vessels rerouting out of the Red Sea, PortWatch
congestion at Suez - timestamped, sourced, confidence-scored."

[Scroll to the Score History + Explainability panel.]

"And this is the part judges care about most: scenario fidelity means
assumptions have to be explicit and testable. Here they are - top drivers,
the exact evidence IDs behind the score, and the scoring formula's
assumptions, openly flagged where they're simulated versus observed. No
black box."

### [1:23-2:08] Scene 4 - Scenario Simulator

[On screen: 9-template dropdown -> select Red Sea Shipping Disruption ->
run -> results.]

"This is the Disruption Scenario Modeller the problem statement calls for.
We've built the exact scenarios this region keeps living through - Hormuz
Partial Closure, Red Sea Shipping Disruption, OPEC+ Supply Cut, Sanctions
Shock - plus we extended the same engine to LNG, coal, fertilizer, and
critical minerals."

[Select Red Sea Shipping Disruption, High severity, 25 days duration,
click Run scenario.]

"Let's simulate a Red Sea shipping disruption against our supply chain
digital twin."

[Results populate.]

"In seconds: 8.9% of supply at risk, a 20.8-day delay, a 24.8% freight cost
spike, a 3.6% fuel price hike, minus 0.13% GDP drag, 86% confidence -
flagged Action Required. It's already traced this through the knowledge
graph to the refineries actually exposed - Reliance Jamnagar and IOCL
Paradip, linked to Bab el-Mandeb and Suez Canal. And it states its
assumptions outright: import share is estimated, exact cargo ownership is
simulated, Cape of Good Hope rerouting adds distance rather than removing
supply. That's cascading impact modeling, done honestly."

### [2:08-2:33] Scene 5 - Recommendation Center

[On screen: load scenario ID -> ranked options table -> SPR plan.]

"That scenario feeds straight into the Adaptive Procurement Orchestrator
and the Strategic Reserve Optimisation Agent - the two hardest asks in the
problem statement."

[Load recommendation.]

"Three ranked, executable alternatives: Iraq via Basra to Jamnagar - 4.5
day delay, 5.2% cost impact, 84% feasibility, Immediate priority. Saudi
Arabia and UAE as contingency. And the SPR call, right below it:
supply-at-risk and delay both stay within normal buffers, so drawdown is
not warranted - 83% confidence, logged against an audit ID. Recommendations
a procurement team can act on within hours, not days - exactly the
executability the evaluation criteria are grading."

### [2:33-2:53] Scene 6 - Reports

[On screen: generate report -> executive brief scrolls.]

"Every scenario and recommendation rolls into an executive brief on
demand - report ID, scenario ID, recommendation ID, audit ID, all
cross-referenced, assumptions restated, exportable straight to PDF. This is
the anticipatory, managed response process the brief asks for, replacing
the reactive scramble."

### [2:53-3:07] Scene 7 - Energy Map

[On screen: Leaflet map with ports/refineries/SPR/routes/chokepoints.]

"Underneath all of it is the Supply Chain Digital Twin - export ports,
import ports, refineries, SPR sites, chokepoints, shipping routes, wellhead
to refinery to distribution. This isn't a static map - it's the live
knowledge graph the risk and scenario engines query directly."

### [3:07-3:18] Scene 8 - Commodity Command Center

[On screen: Crude Oil -> LNG -> Coal -> Fertilizer -> Critical Minerals
tabs.]

"And because the data model is commodity-agnostic, the same engine already
reaches past crude oil - LNG, coal, fertilizer, critical minerals, each
with its own entities, risk scores, and scenario templates. Crude oil is
our fully live MVP; these are architecturally complete and openly marked
illustrative pending live feeds. We'd rather show an honest roadmap than a
faked one."

### [3:18-3:20] Scene 9 - Close

"EnergyShield AI: geopolitical risk, turned into a structured, explainable,
executable response - before disruption hits. Thank you."

## Delivery Notes

- Every scene opens by naming the exact problem-statement capability it
  satisfies (Geopolitical Risk Intelligence Agent, Disruption Scenario
  Modeller, Adaptive Procurement Orchestrator, Strategic Reserve
  Optimisation Agent, Supply Chain Digital Twin) - judges scoring against
  that rubric hear their own five bullet points read back in order.
- Scene 3 and Scene 4's honesty lines ("no black box", stated assumptions)
  are credibility anchors - don't cut them even under time pressure; the
  evaluation focus explicitly rewards "scenario model fidelity - assumptions
  must be explicit and testable."
- If short on time, Scene 3's evidence-modal beat and Scene 8's commodity
  tabs are the safest to trim first. Scenes 2, 4, 5, and 6 are the core
  signal-to-recommendation loop and should stay intact.
