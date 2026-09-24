# Document architecture

How to write the spec, the decisions and the plan so they survive compaction, agent switches and
stale memory. The failure this defends against: a positional reference breaks on insert, a changed
decision leaves the old claim standing as a second truth, a compaction drops the why, and the next
reader propagates the stale version. Every rule below turns one of those into a check.

## Verification tags

Every factual claim carries exactly one tag: `[MV]` machine-verified (you ran it, here), `[DV]`
docs-verified (current official documentation), `[BV]` build-verify (only the build machine can
confirm; a placeholder), `[J]` judgement. Write the tag after the oracle runs, never alongside the
claim — a promissory `[MV]` tells every reader the checking is done. A spike is never `[DV]`. Mechanical
gates validate form, not truth: keep a dated Verification ledger and re-check the claims that leave the
repo as fact (evidence strings, control descriptions, status columns).

## Stable identifiers

Every referenceable unit gets an ID allocated once, never renumbered, tombstoned on removal, cited by
ID never by position. Light spec: `REQ-NNN`, `INV-N`, `ADR-NNNN` inline. Doc set: `REQ-<DOMAIN>-NNN`,
`INV-N`, one file per `ADR-NNNN`, `BP-NNN` steps, `BR-NN` rules, `Phase N`. External IDs (tickets,
CVE, CWE, OWASP) are not yours; do not police them. One handle per separable unit: two units that
would share a handle are one unit; two that cannot merge get separate IDs.

One fact, one home. Restating a fact creates a second copy that drifts; cite the ID instead. The job to
be done lives only in its build step: a requirement states the capability, a decision states the
choice, neither carries Do/Verify content.

## Requirements — EARS

One requirement, one shall, one testable claim, tagged with its form: Ubiquitous "The system shall
…"; Event "When …, the system shall …"; State "While …, the system shall …"; Optional "Where …, the
system shall …"; Unwanted "If …, then the system shall …". `DG-EARS` fails any other opening.

## Decisions and supersession

A decision is appended, never edited. To change one, write a new ADR and set the old file's
frontmatter `status: superseded-by ADR-NNNN`. Every other line still citing the old ID must carry
`superseded-by` or `supersedes`, or `DG-TOMBSTONE` fails it — the corpus scan replaces any
author-maintained list of affected files. An ADR's `Verification` section names the command or test
that proves it holds in code; a supersession is a claim about the code until that grep of the old
symbol comes back empty, and the grep stays as a permanent check.

## Two shapes

`templates/SPEC-light.md` for small-to-medium work: one file, decisions inline. Graduate to
`templates/doc-set/` when the build spans more than a few files, more than one author edits it across
sessions, or invariants need their own log. `CONVENTIONS.md` in the doc set is the project's own
statement of these rules; read it first there.

## Generated views

`build_plan.json` is the only hand-edited source of the plan. `driftguard write build_plan` renders an
index (one line per step, computed status, phase tier-2 evidence) plus one slice file per phase; a
reader opens one slice, never a megafile. The ID register and any table registry (bugs, findings,
coverage) render the same way. Status is computed — a merged PR naming the step, a passing cited test,
a decision reference — never typed. A committed view that differs from its render fails
`DG-REGISTRY-STALE`; a view holding a step its source lost fails `DG-REGISTRY-ORPHAN` and refuses to
write. Never hand-edit a generated file.

## Currency

Prose that describes the present must be true now. A README states what the repo is and does today,
rewritten at each milestone, never appended to; history belongs in git or a changelog. A claim with a
currency word (still, not yet, pending) citing a file is re-checked whenever that file changes
(`DG-CURRENCY`). A count or list derived from a live source is named by its source, not typed as a
number.

## Renames

A rename retrofit rewrites live prose, links, imports and unbuilt-work instructions to the new name.
A dated past-tense record — an incident note, a "ran X and got Y" line — keeps the name that was true
then; changing it makes the record assert something false.

## README

Answer five questions: what it does, why it is useful, how to get started, where to get help, who
maintains it. Internal repos lead with local setup and the gate commands; the bar is "a new hire gets
unblocked from this alone".

## Running the checks

`docs/driftguard.toml` (from `templates/doc-set/driftguard.toml`, or the light example in the package)
declares the ID classes, required sections and registries. `driftguard check --staged` runs in the
pre-commit hook; `driftguard write NAME` regenerates a view. Output lines cite `DG-*` IDs; a failing
check names its root cause in `root-causes.md`.
