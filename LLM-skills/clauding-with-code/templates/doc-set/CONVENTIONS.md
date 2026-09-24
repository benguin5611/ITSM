# CONVENTIONS — <project> doc set

<!-- The one home for this doc set's naming, ID and house-style rules. driftguard.toml enforces them; this file explains them to a human. Read first. -->

## Reading order
1. `SPEC.md` — purpose, exit criteria, invariants, requirements, acceptance, testing guide.
2. `decisions/ADR-NNNN-<slug>.md` — one decision per file; the invariants cite them.
3. `generated/BUILD_PLAN.md` — index of every build step with computed status; the step bodies live in `generated/BUILD_PLAN/phase-NN.md`. Generated from `build_plan.json`; never hand-edit.
4. `DEPENDENCIES.md` — pinned bill of materials.
5. `generated/ID_REGISTER.md` — every ID, its title, home and backlinks. Generated.
6. `binding.md` — the project facts the build skill binds to.

## Identifier classes
Allocated once, never renumbered, tombstoned on removal; cite the ID, never a position.

| Class | Form | Defined where |
| --- | --- | --- |
| Requirement | `REQ-<DOMAIN>-<NNN>` | bold at line start in `SPEC.md`, EARS form |
| Invariant | `INV-<N>` | row in the `SPEC.md` invariants table |
| Decision | `ADR-<NNNN>` | `# ADR-NNNN — title` heading of its own file under `decisions/` |
| Build step | `BP-<NNN>` | `build_plan.json`; rendered as `**BP-NNN (Phase N) — title.**` |
| Build rule | `BR-<NN>` | `build_plan.json` `build_rules`; rendered as `- **BR-NN**` |
| Phase | `Phase <N>` | `## Phase N` heading in the build-plan index |

REQ domains: <list yours>. External IDs (tickets, CVE, CWE, OWASP) are not policed. IDs never appear in shipped code, comments, commit messages or runtime strings.

## Supersession
A decision changes by a new ADR, never an edit: set the old file's frontmatter `status: superseded-by ADR-NNNN`. Any other line citing the old ID must carry `superseded-by` or `supersedes`, or the gate fails it.

## Build plan
Edit `build_plan.json`, then `driftguard write build_plan`. `Status` is computed: `shipped` needs a merged PR naming the ID and a passing `verify_test`; `parked` (a `decision_ref`), `blocked`, `cancelled`, `partial` come from the step's own fields. Every phase names its tier-2 evidence (security, compatibility, regression, interoperability) as a step or an ADR. A known gap is a step, never a list.

## Glossary
| Term | Definition |
| --- | --- |
| <term> | <definition> |
