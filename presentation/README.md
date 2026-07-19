# Presentation Assets (Phase 15)

This directory holds slide-deck source material and a screenshot capture
checklist. It intentionally does not include a rendered slide deck, demo
video, or screenshot image files - those need a human to record/design them
(or a design tool), and fabricating placeholder binary assets here would be
worse than leaving a clear checklist of exactly what to capture and from
where.

## Slide Outline

Use this as the section list for an actual deck (Google Slides/PowerPoint/
Keynote); each maps to one demo beat in
[`../docs/DEMO_SCRIPT.md`](../docs/DEMO_SCRIPT.md).

1. **Title** - EnergyShield AI: AI-Driven Energy Supply Chain Resilience
2. **Problem** - import-dependent economies (India crude oil MVP) can't see
   disruption risk, impact, or response options in one place
3. **Architecture** - component diagram from
   [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
4. **Digital twin + knowledge graph** - screenshot of the Energy Map page
5. **Signal to structured event** - screenshot of the Dashboard's latest
   events panel, or the seeded Red Sea alert from the demo script
6. **Risk scoring with explainability** - screenshot of Risk Monitor,
   including the Explainability panel showing top drivers/evidence
7. **Scenario simulation** - screenshot of Scenario Simulator with a run
   result
8. **Procurement + SPR recommendations** - screenshot of Recommendation
   Center
9. **End-to-end automation** - the Phase 10 orchestration diagram (signal
   -> extraction -> graph -> risk -> scenario -> recommendation, all
   automatic, per `backend/orchestration/workflows.py::run_full_pipeline`)
10. **Continuous learning** - screenshot of Learning Center (historical
    cases, backtest metrics, model versions)
11. **Multi-commodity roadmap** - Commodity Command Center screenshot +
    the rollout table from
    [`../docs/MULTI_COMMODITY_ROADMAP.md`](../docs/MULTI_COMMODITY_ROADMAP.md)
12. **What's real vs. illustrative** - one slide stating plainly: crude oil
    is real seed data; LNG/coal/fertilizer/critical-minerals entities are
    illustrative (`is_simulated: true`); Neo4j/Postgres run in
    graceful-degradation mode in a demo without them started
13. **Closing** - resume-ready description from
    `ENERGYSHIELD_IMPLEMENTATION_PLAN.md`'s Phase 15 section

## Screenshot Capture Checklist

Run `docker-compose up --build` (or the frontend alone with
`VITE_USE_MOCK_DATA=true`), then capture, at 1280x800 or larger:

- [ ] Dashboard (`/`)
- [ ] Risk Monitor (`/risk`) with a corridor card selected and the
      Explainability panel populated
- [ ] Scenario Simulator (`/scenarios`) after running `HORMUZ_PARTIAL_CLOSURE`
- [ ] Recommendation Center (`/recommendations`) for that scenario's id
- [ ] Energy Map (`/map`) with the Leaflet map rendered
- [ ] Knowledge Graph Explorer (`/graph`) for `CHK_HORMUZ`
- [ ] Learning Center (`/learning`) after running a backtest
- [ ] Reports (`/reports`) showing the generated Markdown brief
- [ ] Commodity Command Center (`/commodities`) with LNG selected

## Demo Video

Record narrating [`../docs/DEMO_SCRIPT.md`](../docs/DEMO_SCRIPT.md) while
clicking through the screenshots above in order; 3-5 minutes per the
script's own framing.
