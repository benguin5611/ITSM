# Discovery gate — BLOCKING pre-build checklist (no code until signed off)

The gate is not advisory. **No code is written** until the five artefacts below exist, are
spot-checked, and the human has signed off. The gate exists to surface what will bite you *before*
a line is committed — coupling you assumed away, assumptions you never checked, an environment that
behaves nothing like the happy path, names that collide with what's already there, and contract
breaks nobody planned for. Produce all five, present them, and **stop for explicit human approval.** Concrete tools, commands, and stack specifics → [`project-binding.md`](project-binding.md).

## 1. Dependency-coupling map

For **every** component you intend to build on that is labelled "shared", "generic", "reusable", or
"common", trace what it is *actually* coupled to before you rely on it. "Generic" is a claim, not a
fact — verify it.

- [ ] List every shared/generic component the change will build on or extend.
- [ ] For each, trace the **real** couplings: who calls it, what data it reads/writes, what
      lifecycle/ownership it sits in, what it assumes about its caller.
- [ ] Surface **hidden invariants** — ordering, nullability, tenancy/scoping, transaction
      boundaries, idempotency, retry behaviour — that are not in the signature but are load-bearing.
- [ ] Map the **blast radius**: cross-repo consumers, generated code, frontend/clients, anything
      downstream that a change would break.
- [ ] Flag every component that is **not as generic as assumed** — coupled to one caller, one tenant,
      one feature, one data shape.
- [ ] For each, record a decision: **build on it as-is** / **decouple first** / **build new**. Each
      decision cites the coupling evidence that drove it.

## 2. Assumptions register

Every load-bearing assumption stated explicitly. An unstated assumption is an unguarded failure.

- [ ] Enumerate every assumption the build rests on — about behaviour, data, environment, contracts,
      other teams, and "it already works like X".
- [ ] Tag each **verified** or **unverified**. Nothing ships as "probably".
- [ ] For each, record the **exact check** that confirms it (the command, the query, the test, the
      doc, the person to ask) — not "we'll find out", a specific falsifiable check.
- [ ] Record **who/what confirms it** and when (you, the human, a tool, a teammate).
- [ ] Every unverified assumption is either verified before build, or explicitly accepted as a risk
      by the human at sign-off. No silent unknowns cross the gate.

## 3. Environmental / CI pre-mortem

Model the **real operating environment**, not the demo. Most expensive failures live in how the
system behaves end-to-end under real identity, mail, network, and load — not in the unit you wrote.

- [ ] Walk each real-world subsystem and write down how it *actually* behaves end-to-end: **mail**
      (delivery, themed templates, real inboxes, spam), **auth/identity** (real realm/roles, token
      lifetimes, MFA, anonymous users), **network** (latency, timeouts, retries, partial failure),
      **load/concurrency** (parallel callers, races, idempotency), **data/tenancy** (scoping,
      row-level tenancy, seed drift between local and real).
- [ ] Answer the **"what will bite us in the real environment?"** prompts:
      - What does this depend on that is faked, stubbed, or absent locally?
      - What behaves differently under real auth/identity than under a dev shortcut or bypass flag?
      - What only fails under concurrency, retries, or real network conditions?
      - What config/secret/template exists in the real environment but not locally (and vice versa)?
      - What seed/state drift exists between the local mirror and the real target?
- [ ] **Stand up a local mirror of the CI/CD pipeline** — same commands, same tool versions —
      **before the first commit**, so CI failures surface locally instead of on push. Verify the
      mirror reproduces a known CI step green.
- [ ] Record the gaps the mirror **cannot** reproduce (real mail, real identity provider, real load)
      and how each will be exercised before ship.

## 4. Naming, terminology & rename decisions

Names are decided **here, at planning time** — not retrofitted. Renaming an existing file, service,
procedure, endpoint, or field after the build is N-layer rework (contract/schema → generated code →
handlers → access-control references → frontend → docs); deciding it up front is free.

- [ ] Write a **canonical glossary** — one row per term the feature introduces, with its definition.
- [ ] For every new term, check whether the name **collides with or sits near an existing,
      similarly-named thing** in the tree. If a concept lives near an existing one that shares a word,
      **disambiguate all of them explicitly** in the glossary (the new one *and* the existing ones) —
      ambiguous names quietly diverge mid-build and force a confusing retrofit.
- [ ] Decide every **rename of an existing file / service / procedure / RPC / field** now. For each,
      list the **layers it cascades through** so the cost is visible and the rename is done in one
      deliberate pass, not discovered piecemeal.
- [ ] **Create the parent tracking issue now** (an epic for a feature, a single issue sized to small
      work) — *before any code* — so its ID exists for the branch and the very first commit. Decide the
      **branch / commit / PR ↔ ticket-id convention** (ID in the branch prefix, in every commit, in the
      PR title) and cut the branch with the ID. Creating the ID first makes the link native; retrofitting
      it onto existing commits means rewriting history. See [`work-tracking.md`](work-tracking.md). (The
      full child hierarchy is fleshed out later, once the spec + PR plan are signed off.)
- [ ] Record the glossary + the rename inventory as a gate artefact the human signs off.

## 5. API / contract surface & breaking-change budget

Breaking changes are a **first-class** planning concern, not something discovered at CI or by a
consumer. Inventory the contract before touching a schema.

- [ ] Inventory the **API / contract surface** the change touches: RPCs, messages, fields, enums,
      HTTP routes, DB columns, event shapes, public types.
- [ ] Identify **what each consumer actually binds to** — an HTTP route, a proto/RPC symbol, a JSON
      field name, a DB column. A rename is *free* on layers nobody binds to and *breaking* on the ones
      they do; map this before renaming so you break only what you mean to.
- [ ] Run the **breaking-change linter against the release baseline as the oracle** (not source-text
      reasoning, not grep) — and **read the policy in force**: the policy changes both what counts as a
      break and the correct fix.
- [ ] **Never reuse or renumber a field.** Deprecate it in place at its original number and add the new
      meaning at a fresh number. Under a strict policy you may not even delete-and-reserve — the field
      must physically remain. Do not repopulate an old field with new-meaning data for "compatibility":
      a semantic change behind the same name misleads consumers regardless.
- [ ] Enumerate each break as a **breaking-change ledger** (one row per break: what breaks, who it
      affects, the fix/mitigation) and decide consciously per break: **accept** (no live consumers,
      pre-warn) or **bridge** (keep the old surface alive alongside the new). Record it in the spec.

## 6. Filterability & observability design

Two design properties that are expensive to retrofit — decide them before the schema or handler shape is fixed.

**Filterability:**
- [ ] For every new data field or entity attribute: will users need to filter by this value in the platform? State the decision explicitly — do not leave it implicit.
- [ ] Encrypted or PII fields are **non-filterable by design** (the platform cannot filter on ciphertext). If a field is both sensitive and needs to be filterable, this is a design conflict that must be resolved at the gate — not after the migration.
- [ ] Confirm the platform's filtering capability supports the data type and cardinality of each field marked filterable. High-cardinality free-text is rarely filterable well; structured enum-like values are. Decide the field type accordingly.
- [ ] Record each filterability decision in the spec so the next developer knows it was deliberate.

**Observability:**
- [ ] For every new Connect handler or background job: what Honeycomb attributes will it emit? Plan this as a first-class design output. At minimum: tenant ID, primary entity being operated on, and operation result (success / error code).
- [ ] Confirm the existing trace/span structure in similar handlers, and use it as the reference — don't invent a new attribute naming convention without checking what's already there.
- [ ] Any handler touching a new or high-risk code path must add structured span attributes (not just a log line) so it's queryable in production.

## Exit criteria

- All five artefacts exist, are written to disk, and have been spot-checked by you (not trusted
  from a sub-agent — verify the load-bearing claims yourself).
- Every "generic" component has a build-on / decouple / build-new decision backed by coupling
  evidence.
- Every assumption is verified, or its risk is explicitly accepted by the human.
- The canonical glossary + rename inventory are decided, and the breaking-change ledger is enumerated
  with an accept/bridge decision per break.
- The local CI mirror reproduces a known-green pipeline step.
- No open question remains that would change the design.

## Human checkpoint

Present all five — the dependency-coupling map, the assumptions register, the environmental/CI
pre-mortem, the glossary + rename inventory, and the breaking-change ledger — together with the
recommendations and accepted risks. **Stop for explicit sign-off.** Do not write
code until you have it. If discovery surfaces something that changes the design — a "generic"
component that must be decoupled, an assumption proven false, an environmental constraint that
reshapes the approach — **loop back to design**, do not push through. Re-entering the gate after a
design change is cheaper than unwinding committed code.
