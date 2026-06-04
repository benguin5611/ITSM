# Discovery gate — BLOCKING checklist (run before any expensive fan-out)

The gate is not advisory. Work through it, present the result, and **stop for explicit human sign-off** before launching a heavy pass.

1. **Artefact & goal.** What exactly is under review (spec / test-suite / design / code)? What does "done" look like for this pass?
2. **Ground truth.** Is there a fresh, spot-checked code map at a recorded commit? Is the branch stable, or moving? (If moving — freeze or re-confirm `HEAD` at launch.)
3. **Assumptions surfaced.** List the load-bearing assumptions the review will rest on; mark which are verified vs unverified.
4. **Shared / generic-component coupling.** Map what shared or "generic" components the change touches and what else depends on them — the blast radius. Cross-repo / generated-code / frontend consumers count.
5. **Settled decisions loaded.** Is the canonical decision record primed so nothing settled is re-raised?
6. **Lens selection.** Which lenses for this scope (see `composition-map.md`)? Interactive, or does it warrant the heavy bundled workflow?
7. **Cost estimate.** Agents, approximate tokens, wall-clock. Proportional to the explicit ask — a quick check is a few agents; "be comprehensive" is a larger pool.
8. **Resilience pre-flight.** If running the workflow: is every `agent()` bounded (`withDeadline`/`critical`)? What are the expected output artefacts and the watchdog deadline?
9. **Sign-off.** Present 1–8 and get explicit approval. Do not fan out until you have it.
