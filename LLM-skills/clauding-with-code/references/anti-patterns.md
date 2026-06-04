# clauding-with-code — failure catalogue → anti-patterns

The mistakes this skill exists to prevent. Each one was paid for in a real build; each is generalised into an anti-pattern with its symptom, why it bites, and what to do instead. (Process only — no project, stack, or feature specifics. For the concrete real-world instance of each, see `references/project-binding.md`.)

## A1. Assumed-generic is a trap
**Symptom:** you lean on a "shared" or "generic" component because the name promises it is reusable and decoupled.
**Why it bites:** the thing is quietly coupled to assumptions you didn't trace — a tenancy model, an auth context, a data shape — and it does the wrong thing in your case without erroring loudly.
**Instead:** before depending on anything labelled generic, trace what it is actually coupled to (callers, context it reads, side effects). Treat "generic" as a claim to verify, not a given. See `references/project-binding.md`.

## A2. Modelling the happy path, not the real operating environment
**Symptom:** the design works end-to-end in the obvious flow, so it is declared done.
**Why it bites:** the failure modes live in how mail filters, auth, networks and load actually behave — e.g. link-sandboxing mail security that auto-fetches a one-click link before the human ever sees it, retries, timeouts, clock skew. The happy path never exercises any of these.
**Instead:** enumerate the real operating environment (mail, auth, network, concurrency, load) and design for its failure modes, not the demo. See `references/project-binding.md`.

## A3. Self-referential testing
**Symptom:** the test suite runs against your own code in a bespoke local rig and goes green.
**Why it bites:** green against a setup you built to your own assumptions proves only that the code matches your assumptions — not that it works where it will run. Environment, config and integration drift go undetected.
**Instead:** test against a production-replica frequently, early, and fail fast on divergence. A passing bespoke-local run is not evidence of correctness. See `references/project-binding.md`.

## A4. Skipping linters / not mirroring CI locally
**Symptom:** you push and let CI be the first place a lint or build failure surfaces; hooks get bypassed to "move faster".
**Why it bites:** the feedback loop balloons from seconds to minutes, failures arrive after context-switch, and bypassed hooks let broken code land. Never skip pre-commit hooks.
**Instead:** run the same linters/build/tests locally that CI runs, before pushing; keep hooks on. CI should confirm, not discover. See `references/project-binding.md`.

## A5. Silent hangs
**Symptom:** a monolithic, unbounded long-running step stalls with no output and no notification; only a human happening to look notices.
**Why it bites:** an unbounded step that wedges costs the whole run and gives no signal to act on — you can't tell slow-but-alive from dead.
**Instead:** make every long step bounded by a deadline and loud on stall (abort with a resume hint, plus a liveness watchdog). See `references/orchestration-economy.md` and `references/project-binding.md`.

## A6. Read-all/write-all monoliths
**Symptom:** one agent reads everything, then writes everything, in a single pass.
**Why it bites:** it is unbounded, un-parallelisable, hard to resume, and a single failure forces a full restart.
**Instead:** decompose into a planner that scopes the work plus waved writers each owning a bounded slice. See `references/orchestration-economy.md` and `references/project-binding.md`.

## A7. Tight fan-out deadlines that count queue time
**Symptom:** fan-out agents are given deadlines that start ticking while they sit queued, so a slow queue trips mass false-timeouts on agents that never ran.
**Why it bites:** you abort live, healthy work and the failure looks like a code problem when it is a scheduling artefact.
**Instead:** wave-batch large fan-outs, use generous backstops, and rely on a liveness watchdog (transcript still growing = alive) rather than a wall-clock that counts queue time. See `references/orchestration-economy.md` and `references/project-binding.md`.

## A8. Re-running the whole monolith to recover a small failed tail
**Symptom:** one late sub-task fails, so the entire long run is restarted from the top.
**Why it bites:** it throws away all the completed work and multiplies cost and wall-clock for a small remainder.
**Instead:** finish the tail cheap — resume from cache and re-run only the failed remainder. See `references/orchestration-economy.md` and `references/project-binding.md`.

## A9. Trusting memory of "what changed" when splitting a branch into PRs
**Symptom:** you reconstruct the PR split from recollection of what you touched, re-typing files from memory.
**Why it bites:** memory drifts; files get dropped, duplicated, or subtly altered, and there is no check that the split is complete.
**Instead:** make git the completeness oracle — partition by file, prove the partition is exhaustive and disjoint, transfer exact bytes (`git checkout F`), and assert the invariant that base + all PRs equals the source branch (empty diff). See `references/project-binding.md`.

## A10. Fragmenting the deliverable spec across sibling docs
**Symptom:** the spec is spread across many sibling documents the reader must chase to assemble the whole picture.
**Why it bites:** no single source of truth, claims drift between docs, and reviewers can't tell what is current or complete.
**Instead:** consolidate into one comprehensive spec plus minimal companions; the spec is the canonical artefact, companions only support it. See `references/project-binding.md`.

## A11. Shipping without a testing guide
**Symptom:** the deliverable carries a test-status ledger and that is called the testing story.
**Why it bites:** a ledger records what passed; it does not tell a new person how to run, replicate, or extend the tests. The knowledge leaves with you.
**Instead:** ship an actual testing guide (how to set up, run, and verify) alongside the status ledger — a ledger is not a guide. See `references/project-binding.md`.

## A12. Leaving working clutter behind
**Symptom:** intermediate artefacts, scratch files and resume scaffolding are left in place once the work is done.
**Why it bites:** the next reader can't tell live from dead, stale files get mistaken for current truth, and the repo accumulates noise.
**Instead:** on completion, archive intermediate artefacts and leave only the canonical deliverables. See `references/project-binding.md`.

## A13. Spec/docs that overstate
**Symptom:** the spec asserts behaviour, guarantees or coverage that the code does not actually provide.
**Why it bites:** confident prose ungrounded in code misleads reviewers and bakes false assumptions into downstream work; code wins every time.
**Instead:** ground every load-bearing claim at a real reference (file, function, test) and cut anything you can't anchor. Code is the source of truth, not the doc. See `references/project-binding.md`.

## A14. Over-orchestration
**Symptom:** a large agent swarm running for many hours is spun up for work a small, proportionate run would have done.
**Why it bites:** wall-clock and tokens are first-class constraints; a heavyweight run burns both, adds coordination failure modes, and rarely beats a focused one.
**Instead:** default to a small proportionate budget sized to the task; reserve heavy fan-out for explicit opt-in. See `references/orchestration-economy.md` and `references/project-binding.md`.

## A15. Project-specific language leaking into reusable artefacts
**Symptom:** reusable artefacts (skills, references, templates) carry company/stack/feature names, plus numbered or parenthetical-bloat headings.
**Why it bites:** the artefact stops being reusable — it reads as one project's notes, dates quickly, and leaks internal detail into things meant to be shared.
**Instead:** keep reusable artefacts project-agnostic with clean headings; push every concrete instance into a single project-specific reference. See `references/project-binding.md`.

## A16. Late / ad-hoc renaming and terminology drift
**Symptom:** the canonical names are never settled up front, so the build and its docs grow against ambiguous terms — and a new concept ends up sharing a word with two unrelated existing things before anyone notices.
**Why it bites:** disambiguating after the fact forces a rename that cascades through every layer (schema → generated code → handlers → access-control references → frontend → docs), plus a stale-doc cleanup — pure rework, and a fertile source of confusion mid-build. Worse, an undecided rename doesn't resolve once: it **re-opens repeatedly** (a first rename, then a second to a "better" name later), and a rename can land **silently inside an unrelated commit** whose message never mentions it — and partial renames leave divergences (e.g. the symbol renamed but the file holding it not), so the names quietly stop matching.
**Instead:** decide the glossary and every rename of an existing file/service/procedure/field **at the discovery gate**, before code or spec. When a new term lives near an existing similar one, disambiguate all of them explicitly, and check name collisions against the tree first. See `references/discovery-gate-checklist.md` and `references/project-binding.md`.

## A17. Unmanaged API / schema breaking changes
**Symptom:** a contract change (renumbered or reused field, renamed RPC, changed enum, altered route) is made by editing the schema without checking the wire contract — and the break is found at CI, or by a consumer, or not at all.
**Why it bites:** the compatibility surface was never inventoried; reasoning from source text (or grep) misses what the breaking-change tool catches, and reusing a field number silently changes meaning on the wire. Reserving the field can *also* fail under a strict policy that forbids deleting it.
**Instead:** make breaking-change management a planning artefact — diff against the release baseline and run the breaking-change linter **as the oracle** (and read the policy in force); never reuse or renumber a field (deprecate in place, add new at a fresh number); know which identifier each consumer binds to (route vs symbol vs field); enumerate every break with a fix and an accept/bridge decision. See `references/discovery-gate-checklist.md` and `references/project-binding.md`.

## A18. Letting one cheap check stand in for the right verification oracle
**Symptom:** a zero-hit `grep` (or any single cheap check) is treated as proof that a removal/change is safe.
**Why it bites:** grep proves the weakest possible thing — that *this repo's current source text* has no textual match. It says nothing about correctness, about generated or cross-repo consumers, or about the wire contract. The "safe" call is wrong as often as it is right. The same trap applies to the **commit log**: a commit message is not a reliable record of what a commit did to a contract — a rename or a breaking change can land in a commit whose message advertises something else entirely, so reasoning from the log instead of the artefact misses it.
**Instead:** match the verification tool to the artefact class — a removed code symbol → the compiler/linker plus a cross-repo sweep; a dropped DB column → read the actual migration; a proto/API change → the breaking-change linter; a cross-service consumer → an explicit boundary check. One cheap check never substitutes for all of them. See `references/project-binding.md`.

## A19. Fire-and-forget shareable artefacts
**Symptom:** something handed out to a party — a link, token, key, or share — is minted and forgotten, with no way to see it later or take it back.
**Why it bites:** anything you issue is a standing credential; if it isn't enumerable and revocable, you can't audit who holds access or withdraw it when you must, which is a security and privacy liability (directive #1).
**Instead:** design every shareable artefact as a first-class object — enumerable, inspectable, and revocable — from the start, not a side effect of the flow that creates it. See `references/project-binding.md`.

## A20. Tracking created late — then reinvented, mis-scoped, or skipped
**Symptom:** the tracking issue is created *after* code already exists (so early branches/commits carry no ID), or the tracker is ignored (work invisible on the board), or filled from scratch in a different shape than the spec/PR-plan, or blown up into a hundred-card ceremony (or collapsed into one mega-card).
**Why it bites:** if the issue ID doesn't exist before the first commit, the only way to link those commits later is to rewrite history (a force-push that may be disallowed on a shared branch) — so the work silently never appears on the card. A tracker that doesn't mirror the planned work can't show progress or traceability; reinventing the breakdown drifts from the signed-off artefacts; over- or under-decomposition makes the board useless; and non-code workstreams (provisioning, flags, secrets, cleanup) fall through the cracks.
**Instead:** create the parent issue (epic, or an issue sized to the work) **at the gate, before any code**, and cut the branch + write every commit with its ID from commit one. Then project the signed-off spec + PR plan into a proportionate epic→feature→task hierarchy under it, with one workstream mapping 1:1 to the planned PRs and a workstream for non-code readiness; keep cards lean (prose over empty ceremony fields). See `references/work-tracking.md` and `references/project-binding.md`.

## A21. Stale inline copies left behind when a shared list is extracted into a named group
**Symptom:** a literal list (of permissions, procedures, routes, columns, feature flags) is refactored into a named, reusable group — but one or more consumers keep their own older inline copy of that list rather than referencing the group.
**Why it bites:** the inline copies silently diverge. The extracted group later gains a new member that the stale literals never receive, producing a quiet permission/behaviour gap that no compiler catches and only a runtime denial (or a reviewer) surfaces.
**Instead:** treat extracting a shared list as a coupling change, not a local edit — sweep every consumer that held an inline copy and either point it at the group or update it, and record the blast radius in the Phase 0 coupling map. See `references/project-binding.md`.

## A22. Review/process identifiers leaking into shipped code
**Symptom:** internal review and planning identifiers ride into the product tree — finding IDs and test-suite/EARS requirement codes (`U5.1`, `W7.17`, `SEC-20`, `R-IMP-03`), review-process references (`rainbow review C5`, `meta-review`, `dead-code-swarm`), and plan/spec section pointers (`test-suite §9.1`, `(plan §4g)`) baked into doc comments, inline comments, `t.Run(...)` / `it(...)` test names, even filenames (`..._section3_test.go`). It happens because the build loop implements a coded artefact (the finding catalogue or test-suite spec) and the agent copies the requirement's ID straight into the thing it writes.
**Why it bites:** those codes are meaningful only inside the review's own bookkeeping. To the next developer they're noise that points at a document they can't see — they read as load-bearing ("what's W7.17? what was decided?"), invite a fruitless hunt, and quietly date the code to one review pass. They also leak that an AI review process produced the code. The artefact's traceability is not the product's concern.
**Instead:** the spec/finding IDs are **artefact-internal traceability only** — they never travel into anything committed. When you implement a coded requirement, carry the *prose that explains the behaviour*, not its ID: a test name describes what it asserts (`renders the all-items option as a single summary row`), a comment states the invariant (`every failure branch spends the same constant cost`), not the code that filed it. The same applies to commit messages and PR bodies. Sweep for these before each PR (`grep` for the ID shapes and the process words) — and if a sweep removes a code that sat mid-prose, re-read the line so you don't strand its punctuation. (Companion on the review side: meta-code-review's standing finding-ID rule — IDs are bookkeeping, not output.) See `references/project-binding.md`.
