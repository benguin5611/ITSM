# Phase 0 — discovery gate

This is a planning process, not a deliverable. Fill `templates/discovery-gate.md` in a scratch file
under `~/Downloads` (e.g. `~/Downloads/<repo>-discovery-gate.md`), every section filled, sign-off
present. Never write it into the target repo — not `docs/`, not anywhere `driftguard check` or a
commit will pick it up. No code before that. Loop back here whenever building or reviewing reopens a
Phase 0 assumption.

## Before the artefact

1. Read the repo's agent file and README first — the agent file names the binding doc's actual path
   (default `docs/binding.md`, but repos move it). No binding yet: fill `templates/binding.md` with
   the human first; the gate commands, tracker key and merge policy it names are inputs to everything
   below.
2. Question the need. No feature without a stated need; write it in the human's words.
3. Spike to learn, then throw the spike away. Anything relied on from a spike is machine-verified
   against the real system, never docs-verified.

## Filling the sections

Prior art. Adopt a fit tool; if it does not fit, steal its design and build the minimum; stack
complementary tools freely. Search twice for every surface the build introduces: what builds it and
what tests it — different ecosystems, and the second is the one that goes missing. Two candidates
minimum or say why there is one. Before imitating a pattern from a nearby file, check the decision
log for a supersession covering it; match the current shape and flag the file you almost copied.
Search inward too: machinery for a documented capability often exists, unused.

Coupling map. For every component labelled shared or generic, trace who calls it, what context it
reads, what it assumes about tenancy, ordering, transactions, retries. Decide build-on, decouple or
new, citing the coupling you found. A list extracted into a named group is a coupling change: every
consumer holding an inline copy is in the blast radius.

Assumptions. One row per load-bearing assumption with the exact command, query or person that
confirms it. `unverified` rows need the human's `accepted-risk: name, date` or they block the gate.
If the build touches a mechanism the decision log calls superseded, add the row "old mechanism has
zero callers outside a documented shim" and prove it with a grep, not the log's prose.

Gate commands and environment. The gate is the binding's commands, run locally on every unit; a CI
workflow, if one exists, re-runs them and is never the gate. Record what the replica cannot reproduce
(mail, identity, network, load, seed drift) and how each is exercised before ship. Record the target
OS and runtime versus the dev machine: same command names on a different OS is not parity.

Names. A glossary row per new term, disambiguated from anything nearby that shares a word. Every
rename of an existing thing, with the layers it cascades through, decided here — a rename left to the
build re-opens repeatedly and lands silently inside unrelated commits.

Contract and breaking-change budget. Inventory the surface (RPCs, fields, routes, columns, events,
public types) and what each consumer binds to. Run the binding's breaking-change oracle against the
release baseline; it is the only judge. Never reuse or renumber a field. One row per break with an
accept or bridge decision.

Filterability and observability. Per new field: filterable or not, and whether the platform can
filter that type at that cardinality; encrypted or personal fields are not filterable by design. Per
new handler or job: the span attributes it emits, matching the existing convention.

Threats and privacy. A STRIDE pass sized to the change and a personal-data inventory
(`security-privacy.md`). Every high or critical threat has a disposition row citing an ADR or a test.

## The checkpoint

Before presenting, re-read the artefact and pull out every call a reasonable person could make
differently: scale, fidelity, placement, verification depth, any two options that both fit. Each goes
in Open forks as a question with your recommendation and reasoning; the human's answer goes in the
Decision cell in their words. Do nothing downstream of an unanswered fork: no ID allocation, no
placeholder entry, no branch. Record what was declined so a later pass does not resurrect it.

Present all sections, the forks and the accepted risks together and stop. On sign-off, create the
tracker issue and cut the branch with its key (binding Tracker) — before the first commit, so every
commit links natively. If discovery changed the design, revise and re-present; re-entering the gate is
cheaper than unwinding code. The `~/Downloads` file is scratch: never `git add` it, and it never
appears in a PR — its content lives on in the human's decisions and, from Phase 1, in `docs/SPEC.md`.
