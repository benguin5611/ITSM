// meta-code-review — generalised heavy-pass orchestrator (opt-in, after the discovery gate is signed off).
// Runs the expensive review lenses (security sweep, dead-code swarm, grudge adjudication) and a final
// synthesis, then writes a versioned artefact + changeset. Default review is INTERACTIVE (SKILL.md);
// this script is only for the heavy fan-out, and only on explicit opt-in with a cost estimate shown.
// ORCHESTRATION ECONOMY (SKILL.md, load-bearing): this is the COMPREHENSIVE mode. The lean default does
// NOT run this — it selects a high-signal subset, batches small inputs per agent, one analyst per item,
// targeting a handful of agents (an order of magnitude cheaper than a sprawling many-agent run). Even here,
// prefer batching inputs into a finder over one-agent-per-artefact; "mine the whole journey" governs what you READ, not agent count.
//
// Launch: Workflow({ scriptPath: ".../meta-code-review/scripts/meta-code-review.workflow.js", args: { ...config } })
// Recover a stall: Workflow({ scriptPath, resumeFromRunId }) — cached agents replay; only the failed step re-runs.
//
// args (all optional; supply what the pass needs):
//   artefact   path to the artefact under review (spec / test-suite / design)
//   codemap    path to the freshly-regenerated, spot-checked code map (ground truth)
//   repo       repo root the agents may read (root strictly inside it)
//   outDir     output directory (default the artefact's dir)
//   priors     path(s) to the decision record / prior-decisions to prime with
//   secRefs    dir of security reference files (owasp/cwe/sinks/boundaries — see project-binding.md)
//   deadcodePartitions  [{key, brief}] slices for the dead-code swarm
//   focus      one-line "priority surface" string folded into every prompt

export const meta = {
  name: 'meta-code-review-heavy',
  description: 'meta-code-review heavy passes: grounded security sweep + dead-code swarm + grudge adjudication + guarded synthesis of a versioned artefact',
  phases: [
    { title: 'Security Inventory' },
    { title: 'Security Sweep' },
    { title: 'Security Synthesis' },
    { title: 'Dead Code Sweep' },
    { title: 'Grudge Review' },
    { title: 'Synthesis' },
  ],
}

// ---- §5a NO SILENT HANG — load-bearing guards (battle-tested). ----
// withDeadline bounds any promise; inside parallel()/pipeline() a rejection becomes null and the
// barrier proceeds. critical() bounds a sequential single-point-of-failure step, retries ONCE,
// then aborts LOUDLY with a resume hint rather than hanging silently.
const DEADLINE_MS = (args && args.deadlineMs) || 8 * 60 * 1000 // 8 min/attempt — generous; fails fast on a true hang
function withDeadline(p, ms, label) {
  if (typeof setTimeout !== 'function') return Promise.resolve(p) // sandbox without timers: degrade gracefully
  let t
  const timeout = new Promise((_, rej) => { t = setTimeout(() => rej(new Error('DEADLINE: "' + label + '" exceeded ' + ms + 'ms')), ms) })
  return Promise.race([
    Promise.resolve(p).then(v => { clearTimeout(t); return v }, e => { clearTimeout(t); throw e }),
    timeout,
  ])
}
async function critical(label, ms, mk) {
  for (let attempt = 1; attempt <= 2; attempt++) {
    try { return await withDeadline(mk(), ms, label) }
    catch (e) {
      log('CRITICAL "' + label + '" attempt ' + attempt + '/2 failed: ' + (e && e.message))
      if (attempt === 2) {
        throw new Error('FAIL-FAST: critical step "' + label + '" stalled/failed twice (' + ms + 'ms each). '
          + 'Root-cause the step before resuming again (bound it, or split a one-shot synthesis into sectioned '
          + 'writes); recover via Workflow({scriptPath, resumeFromRunId}) — cached agents replay, only this step re-runs.')
      }
    }
  }
}
// guarded fan-out helper: wrap a thunk so a slow agent degrades to null instead of wedging the barrier.
const bounded = (label, thunk) => () => withDeadline(thunk(), DEADLINE_MS, label).catch(e => { log('fan-out "' + label + '" dropped: ' + (e && e.message)); return null })

// ---- config ----
const A = args || {}
const ARTEFACT = A.artefact, CODEMAP = A.codemap, REPO = A.repo
const OUTDIR = A.outDir || (ARTEFACT ? ARTEFACT.replace(/\/[^/]*$/, '') : '.')
const PRIORS = [].concat(A.priors || []).join(', ')
const SECREFS = A.secRefs || ''
const FOCUS = A.focus ? ('\n\nPRIORITY SURFACE: ' + A.focus) : ''
const GROUND = [
  'You are a sub-agent in a grounded meta-code-review. CODE WINS: the running code under ' + REPO + ' is the source of truth; the artefact lags it. Describe what IS; never fabricate; cite file:line.',
  'Artefact under review: ' + ARTEFACT,
  'Ground-truth code map (spot-checked): ' + CODEMAP,
  PRIORS ? ('Prior decisions — settled, do not re-litigate: ' + PRIORS) : '',
  'Root every read strictly inside ' + REPO + '.' + FOCUS,
].filter(Boolean).join('\n')

// ---- security sweep (inventory -> owasp/cwe in parallel -> synthesis) ----
async function security() {
  const inventory = await critical('sec-inventory', DEADLINE_MS, () => agent(
    GROUND + '\n\nYOUR ROLE: scoped security INVENTORY (no judgments). Entry points + auth gates; dangerous sinks; trust boundaries (row-level/tenant isolation, request context, bypass lists, error-code preservation). '
    + (SECREFS ? ('Read ' + SECREFS + '/sinks.md and ' + SECREFS + '/boundaries.md. ') : '') + 'Output three markdown tables.',
    { label: 'sec-inventory', phase: 'Security Inventory', agentType: 'Explore' }))
  const [owasp, cwe] = await parallel([
    bounded('sec-owasp', () => agent(GROUND + '\n\nYOUR ROLE: OWASP API/Web sweep over the surface. '
      + (SECREFS ? ('Load ' + SECREFS + '/owasp-api.md + ' + SECREFS + '/owasp-web.md. ') : '')
      + 'For each concern: where in code AND whether the artefact covers it (cite id). Output MISSING/WEAK requirements (EARS), severity-tagged. Gaps only.\n\nINVENTORY:\n' + inventory,
      { label: 'sec-owasp', phase: 'Security Sweep' })),
    bounded('sec-cwe', () => agent(GROUND + '\n\nYOUR ROLE: CWE sweep (authn, authz, crypto/secrets, concurrency, resource/DoS, error-handling/info-disclosure, session/token, logging). '
      + (SECREFS ? ('Load ' + SECREFS + '/cwe-applicable.md. ') : '')
      + 'State where each lives and whether the artefact covers it. Output MISSING/WEAK requirements (EARS) with CWE id.\n\nINVENTORY:\n' + inventory,
      { label: 'sec-cwe', phase: 'Security Sweep' })),
  ])
  const synthesis = await critical('sec-synthesis', DEADLINE_MS, () => agent(
    GROUND + '\n\nYOUR ROLE: consolidate into one deduplicated, severity-sorted list of MISSING/WEAK requirements — stable id, EARS text, target section, layer, severity, source (OWASP/CWE), NEW vs STRENGTHEN. List spec-vs-code mismatches to correct under CODE-WINS. Write to ' + OUTDIR + '/security-findings.md and return it.\n\nOWASP:\n' + (owasp || '(dropped)') + '\n\nCWE:\n' + (cwe || '(dropped)'),
    { label: 'sec-synthesis', phase: 'Security Synthesis' }))
  return { inventory, owasp, cwe, synthesis }
}

// ---- dead-code swarm (deterministic API-surface census + parallel finders -> mechanical collator) ----
// The judgement-based finders (partitions) catch unreferenced funcs etc.; they MISS API-surface dead
// code (proto oneof variants / enum values referenced only by generated marshalling — deadcode/staticcheck
// report it "used"). So an exhaustive, deterministic EMITTER CENSUS always runs alongside them. See A12.
async function apiSurfaceCensus() {
  return bounded('deadcode:api-surface-census', () => agent(
    'You run a DETERMINISTIC EMITTER CENSUS over the API surface under ' + REPO + ' (root strictly inside) — not a judgement call. This catches dead code the other finders structurally miss: a proto `oneof` variant or `enum` value is referenced by GENERATED marshalling, so `deadcode`/staticcheck report it "used" while NOTHING non-generated ever constructs it.\n'
    + 'METHOD (be exhaustive, count — do not sample): (1) Enumerate EVERY proto `oneof` variant, EVERY `enum` value, and every audit/event-type constant in scope. (2) For each, grep for NON-generated (exclude generated-marshalling files), NON-test (exclude `_test`) emitters — the code that actually CONSTRUCTS/SETS it. (3) Report a count per identifier. ZERO non-generated emitters = DEAD CANDIDATE (even though it is public API / ships into the published contract). (4) Trigger hardest where the changeset MOVED a capability between paths — census the OLD path explicitly; orphaned-but-still-defined types are the classic leftover.\n'
    + 'Output a table: identifier | file:line of definition | non-generated emitter count | DEAD CANDIDATE? | the exact grep you ran. Then a one-line tally. Include every zero-emitter item as a candidate; the adjudicator decides.',
    { label: 'deadcode:api-surface-census', phase: 'Dead Code Sweep', agentType: 'Explore' }))
}
async function deadCodeSweep() {
  const partitions = A.deadcodePartitions || []
  const preamble = 'You are ONE finder in a dead-code swarm for the surface under ' + REPO + ' (root strictly inside). You only NOMINATE candidates; an adjudicator decides. Always include the reference-check you ran; never flag generated files without saying so. NOTE: a separate census handles API surface (proto oneof/enum) — focus on funcs, methods, vars, types, queries, and wiring.'
  // The census ALWAYS runs (it needs no partitions); the judgement finders run only when sliced.
  const finds = (await parallel([
    () => apiSurfaceCensus(),
    ...partitions.map(p => () => bounded('deadcode:' + p.key, () => agent(
      preamble + '\n\nSLICE: ' + p.brief + '\n\nFor each candidate: identifier + file:line, why you suspect it is dead, and the reference-check you ran. Terse bullets; if clean, say "clean".',
      { label: 'deadcode:' + p.key, phase: 'Dead Code Sweep', agentType: 'Explore' }))),
  ])).filter(Boolean)
  const list = finds
  log('dead-code swarm: ' + list.length + '/' + (partitions.length + 1) + ' slices returned (incl. API-surface census)')
  if (!list.length) return null
  return critical('deadcode-collate', DEADLINE_MS, () => agent(
    'You are a mechanical COLLATOR — no verdicts. Merge + de-duplicate the candidate lists into one clean list grouped by area; keep each item file:line + suspicion + reference-check. Output the consolidated list only.\n\nLISTS:\n' + list.join('\n\n---\n\n'),
    { label: 'deadcode-collate', phase: 'Dead Code Sweep' }))
}

// ---- grudge: adversarial code review + dead-code adjudication ----
// SPLIT into two bounded halves run in PARALLEL. Bundling both heavy jobs into ONE bounded agent
// deterministically blows the deadline (a grudge mega-agent stalled at 8min x2 while genuinely working —
// transcript mid-read, events still growing). Splitting (not just lengthening the deadline) is the
// fix: each half is lighter and they overlap. See anti-patterns.md A1.
async function grudgeCodeReview() {
  return agent(
    GROUND + '\n\nYOUR ROLE — ADVERSARIAL CODE REVIEW (the AI-sceptic engineer). You distrust AI-generated code and want to find what is wrong with it. Be aggressive, specific, HONOURABLE (no fabrication; cite file:line + a concrete failure scenario) and TERRIFIED of a false positive (bring receipts: read the path end to end, quote the code, and actively try to REFUTE your own finding by checking upstream mitigations — validators, interceptors, row-level policies, locks, constraints, clamps — assert only what you failed to refute). Honour CODE-WINS and the priors. Pay particular attention to any comment whose stated behaviour, value or invariant no longer matches the code it sits on. You consider it failure to surface nothing at Medium+, but you MUST admit it honestly rather than manufacture. Output a "## Findings" section ordered by severity: file:line, the quoted code, the failure scenario, the receipts/refutation you ruled out, and confidence.',
    { label: 'grudge-code-review', phase: 'Grudge Review' })
}

async function deadcodeAdjudicate(deadCandidates) {
  return agent(
    GROUND + '\n\nYOUR ROLE — DEAD-CODE FINAL ADJUDICATION. You are the SINGLE final arbiter of the dead-code candidates below; finders only nominate. For each, hunt hard for references the finders missed (other packages, generated code, reflection, build tags, test-only, external/frontend consumers, DI wiring, SQL-by-name, templates); ONE live reference means NOT DEAD; a candidate you cannot prove unreachable defaults to KEEP. EXCEPTION for API-surface census candidates (proto oneof variants / enum values): references from GENERATED marshalling do NOT count as live — these types are always self-referenced by generated code; require a NON-generated, non-test emitter (something that actually constructs/sets the value) or it is DEAD even though it ships as public API. Same false-positive dread and receipts discipline. Output a "## Dead-code adjudication" table (candidate | location | REALLY DEAD? + receipts | REMOVE/KEEP + why | confidence) then a one-line tally.\n\nCANDIDATES:\n' + (deadCandidates || 'none'),
    { label: 'deadcode-adjudicate', phase: 'Grudge Review' })
}

// ---- run ----
const [sec, deadCandidates] = await parallel([bounded('security', () => security()), bounded('deadCodeSweep', () => deadCodeSweep())])
const [grudgeCode, deadAdjud] = await parallel([
  () => critical('grudge-code-review', DEADLINE_MS, () => grudgeCodeReview()),
  () => critical('deadcode-adjudicate', DEADLINE_MS, () => deadcodeAdjudicate(deadCandidates)),
])
const grudgeOut = (grudgeCode || '(grudge code-review step did not complete)') + '\n\n=== DEAD-CODE ADJUDICATION ===\n\n' + (deadAdjud || '(dead-code adjudication step did not complete)')

// Final synthesis is the classic single-point-of-failure — guard it. If it grows too large to finish in one
// turn, split it (a planner that returns the change-list, then per-section authors, then a stitch) — do NOT
// just lengthen the deadline. (This exact step has hung unguarded; the guard converts it to a loud abort.)
const synth = await critical('synthesise', DEADLINE_MS, () => agent(
  GROUND + '\n\nYOUR ROLE: author the NEXT VERSION of the artefact by applying the accepted findings.\n\nINPUTS:\n- Security findings (apply each):\n' + ((sec && sec.synthesis) || '(none)') + '\n\n- Adversarial review + dead-code adjudication (fold confirmed defects as requirements/flags; handle the dead-code table as a changeset appendix, NOT requirements):\n' + (grudgeOut || '(none)') + '\n\nRULES: CODE WINS (correct stale claims to the code map); PRESERVE correct content verbatim with its id; ADD new requirements with fresh non-colliding ids + coverage rows; recompute Counts ACCURATELY (requirement bullets == coverage rows; no duplicate ids); the doc has NO open-questions section — return open items SEPARATELY for the human; append a Changelog + a Requirements-coverage map + a dead-code appendix. FINAL ROI PASS (MANDATORY — run last over EVERY proposed test requirement; coverage-and-findings.md §0): Gate A — if the feature under test is NOT built at the code-map HEAD (a proposed/planned/decided-against primitive), DISCARD it to the "Future (build-gated)" appendix (never a TO IMPLEMENT/@blocked suite row), or note it folds into the task that builds the feature; Gate B (survivors only) — CUT restatement, cross-layer duplicates, framework/generated-code tests and cosmetics, KEEP behavioural + security-property coverage. Most EARS rows are directionally correct yet still not worth writing — discard those. Only survivors enter the artefact. House language/style.\n\nWrite the COMPLETE next version to ' + OUTDIR + '/artefact-next.md and a concise memo to ' + OUTDIR + '/changeset.md. Return ONLY (<250 words): the two paths; before/after counts; change-class tally; the ROI-pass prune count (evaluated N / discarded-no-feature E / discarded-low-ROI F / kept K); and the bullet list of OPEN ITEMS needing a human decision.\n\nArtefact: ' + ARTEFACT + '  Code map: ' + CODEMAP,
  { label: 'synthesise', phase: 'Synthesis' }))

return { securitySynthesis: sec && sec.synthesis, deadCandidates, grudge: grudgeOut, synthSummary: synth }
