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
// Recover a stall: Workflow({ scriptPath, resumeFromRunId, args: { ...config } })
//   NOTE: args must be re-passed on resume — they are not stored between runs.
//
// args (all optional; supply what the pass needs):
//   artefact           path to the artefact under review (spec / test-suite / design)
//   codemap            path to the freshly-regenerated, spot-checked code map (ground truth)
//   repo               repo root the agents may read (root strictly inside it)
//   outDir             output directory (default the artefact's dir)
//   priors             path(s) to the decision record / prior-decisions to prime with
//   secRefs            dir of security reference files (owasp/cwe/sinks/boundaries — see project-binding.md)
//   domainOverlays     path(s) to domain overlay files (e.g. references/domain-backend.md) to include in every
//                      agent's ground context; auto-detect domain at the discovery gate and pass the matching overlay(s)
//   deadcodePartitions [{key, brief}] slices for the dead-code swarm
//   grudgePartitions   [{key, brief}] scoped slices for the adversarial grudge pass; recommended for whole-repo
//                      runs where a single agent cannot complete the review within one deadline (same shape as deadcodePartitions)
//   focus              one-line "priority surface" string folded into every prompt
//   deadlineMs         override per-agent fan-out deadline in ms (default 8 min)
//   synthDeadlineMs    override synthesis/adjudication/grudge deadline in ms (default 12 min)

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
const SYNTHESIS_DEADLINE_MS = (args && args.synthDeadlineMs) || 12 * 60 * 1000 // 12 min for synthesis/adjudication/grudge on larger inputs
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
          + 'writes); recover via Workflow({scriptPath, resumeFromRunId, args: {...}}) — cached agents replay, only this step re-runs. '
          + 'Remember to re-pass args on resume.')
      }
    }
  }
}
// guarded fan-out helper: wrap a thunk so a slow agent degrades to null instead of wedging the barrier.
const bounded = (label, thunk) => () => withDeadline(thunk(), DEADLINE_MS, label).catch(e => { log('fan-out "' + label + '" dropped: ' + (e && e.message)); return null })

// ---- config ----
const A = args || {}
if (!A.repo || !A.artefact) throw new Error(
  'FAIL-FAST: required args (repo, artefact) not received. Pass them via the args parameter. '
  + 'On resume (Workflow({scriptPath, resumeFromRunId})), args must be re-passed alongside resumeFromRunId — they are not stored between runs.')
const ARTEFACT = A.artefact, CODEMAP = A.codemap, REPO = A.repo
const OUTDIR = A.outDir || (ARTEFACT ? ARTEFACT.replace(/\/[^/]*$/, '') : '.')
const PRIORS = [].concat(A.priors || []).join(', ')
const SECREFS = A.secRefs || ''
const DOMAIN_OVERLAYS = [].concat(A.domainOverlays || [])
const FOCUS = A.focus ? ('\n\nPRIORITY SURFACE: ' + A.focus) : ''
const GROUND = [
  'You are a sub-agent in a grounded meta-code-review. CODE WINS: the running code under ' + REPO + ' is the source of truth; the artefact lags it. Describe what IS; never fabricate; cite file:line.',
  'Artefact under review: ' + ARTEFACT,
  'Ground-truth code map (spot-checked): ' + CODEMAP,
  PRIORS ? ('Prior decisions — settled, do not re-litigate: ' + PRIORS) : '',
  DOMAIN_OVERLAYS.length ? ('Domain overlays — read and apply before reviewing: ' + DOMAIN_OVERLAYS.join(', ')) : '',
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
  const synthesis = await critical('sec-synthesis', SYNTHESIS_DEADLINE_MS, () => agent(
    GROUND + '\n\nYOUR ROLE: consolidate into one deduplicated, severity-sorted list of MISSING/WEAK requirements — stable id, EARS text, target section, layer, severity, source (OWASP/CWE), NEW vs STRENGTHEN. List spec-vs-code mismatches to correct under CODE-WINS. Write to ' + OUTDIR + '/security-findings.md and return it.\n\nOWASP:\n' + (owasp || '(dropped)') + '\n\nCWE:\n' + (cwe || '(dropped)'),
    { label: 'sec-synthesis', phase: 'Security Synthesis' }))
  return { inventory, owasp, cwe, synthesis }
}

// ---- dead-code swarm (deterministic API-surface census + parallel finders -> mechanical collator) ----
// The judgement-based finders (partitions) catch unreferenced funcs etc.; they MISS API-surface dead
// code (proto oneof variants / enum values referenced only by generated marshalling — deadcode/staticcheck
// report it "used"). So an exhaustive, deterministic EMITTER CENSUS always runs alongside them. See A12.
// Census is split into two agents to avoid a single context window doing both exhaustive
// enumeration (file-read heavy) and exhaustive grepping (tool-call heavy) — combining them
// reliably blew the deadline on large repos. The enumerator is critical() (no point grepping
// against an empty list); the grep step is bounded() (drops to null on timeout, collator notes it).
async function apiSurfaceCensus() {
  const identifiers = await critical('deadcode:census-enumerate', DEADLINE_MS, () => agent(
    'ENUMERATION ONLY — no grepping. Under ' + REPO + ' (root strictly inside), enumerate EVERY proto `oneof` variant, EVERY `enum` value, and every audit/event-type constant defined in the codebase. For each: identifier name | file:line of definition | type (oneof-variant / enum-value / audit-constant). Output ONLY a pipe-separated list — no analysis, no counts, no commentary. Include 100% of identifiers; never sample or summarise.',
    { label: 'deadcode:census-enumerate', phase: 'Dead Code Sweep', agentType: 'Explore' }))
  if (!identifiers) return null
  return bounded('deadcode:census-grep', () => agent(
    'EMITTER CENSUS — grep only, no new enumeration. The complete identifier list is below. For EACH identifier: (1) grep under ' + REPO + ' for NON-generated (exclude *.pb.go, *.gen.go, and any file whose path contains "gen/"), NON-test (exclude *_test.go) emitters — code that actually CONSTRUCTS or SETS the value; (2) record the count; (3) note the exact grep command you ran. ZERO non-generated emitters = DEAD CANDIDATE (even though it ships as public API). Trigger hardest where the changeset MOVED a capability between paths — census the old path explicitly. Output a table: identifier | file:line of definition | non-generated emitter count | DEAD CANDIDATE? | grep used. Then a one-line tally. Include every zero-emitter item; the adjudicator decides.\n\nIDENTIFIERS:\n' + identifiers,
    { label: 'deadcode:census-grep', phase: 'Dead Code Sweep' }))()
}
async function deadCodeSweep() {
  const partitions = A.deadcodePartitions || []
  const preamble = 'You are ONE finder in a dead-code swarm for the surface under ' + REPO + ' (root strictly inside). You only NOMINATE candidates; an adjudicator decides. Always include the reference-check you ran; never flag generated files without saying so. NOTE: a separate census handles API surface (proto oneof/enum) — focus on funcs, methods, vars, types, queries, and wiring.'
  // The census ALWAYS runs (it needs no partitions); the judgement finders run only when sliced.
  const finds = (await parallel([
    () => apiSurfaceCensus(),
    ...partitions.map(p => bounded('deadcode:' + p.key, () => agent(
      preamble + '\n\nSLICE: ' + p.brief + '\n\nFor each candidate: identifier + file:line, why you suspect it is dead, and the reference-check you ran. Terse bullets; if clean, say "clean".',
      { label: 'deadcode:' + p.key, phase: 'Dead Code Sweep', agentType: 'Explore' }))),
  ])).filter(Boolean)
  log('dead-code swarm: ' + finds.length + '/' + (partitions.length + 1) + ' slices returned (incl. API-surface census)')
  if (!finds.length) return null
  return critical('deadcode-collate', DEADLINE_MS, () => agent(
    'You are a mechanical COLLATOR — no verdicts. Merge + de-duplicate the candidate lists into one clean list grouped by area; keep each item file:line + suspicion + reference-check. Output the consolidated list only.\n\nLISTS:\n' + finds.join('\n\n---\n\n'),
    { label: 'deadcode-collate', phase: 'Dead Code Sweep' }))
}

// ---- grudge: adversarial code review + dead-code adjudication ----
// The code review supports optional grudgePartitions for whole-repo runs where a single agent cannot
// complete the adversarial pass within one deadline (see A1 + A13). When partitions are supplied,
// each slice runs in bounded parallel and a merge step consolidates them. When omitted, a single
// critical() agent handles the whole scope (appropriate for targeted / scoped reviews).
async function grudgeCodeReview() {
  const partitions = A.grudgePartitions || []
  const reviewPrompt = GROUND + '\n\nYOUR ROLE — ADVERSARIAL CODE REVIEW (the AI-sceptic engineer). You distrust AI-generated code and want to find what is wrong with it. Be aggressive, specific, HONOURABLE (no fabrication; cite file:line + a concrete failure scenario) and TERRIFIED of a false positive (bring receipts: read the path end to end, quote the code, and actively try to REFUTE your own finding by checking upstream mitigations — validators, interceptors, row-level policies, locks, constraints, clamps — assert only what you failed to refute). Honour CODE-WINS and the priors. Pay particular attention to any comment whose stated behaviour, value or invariant no longer matches the code it sits on. You consider it failure to surface nothing at Medium+, but you MUST admit it honestly rather than manufacture. Output a "## Findings" section ordered by severity: file:line, the quoted code, the failure scenario, the receipts/refutation you ruled out, and confidence.'
  if (!partitions.length) {
    return critical('grudge-code-review', SYNTHESIS_DEADLINE_MS, () => agent(
      reviewPrompt, { label: 'grudge-code-review', phase: 'Grudge Review' }))
  }
  const slices = (await parallel(partitions.map(p => bounded('grudge:' + p.key, () => agent(
    reviewPrompt + '\n\nSCOPE FOR THIS SLICE (stay within it): ' + p.brief,
    { label: 'grudge:' + p.key, phase: 'Grudge Review' }))))).filter(Boolean)
  log('grudge: ' + slices.length + '/' + partitions.length + ' slices returned')
  if (!slices.length) return null
  return critical('grudge-merge', SYNTHESIS_DEADLINE_MS, () => agent(
    'MERGE ONLY — combine the adversarial review slices below into one deduplicated "## Findings" section ordered by severity. Make no new findings; cite file:line from the originals.\n\n' + slices.join('\n\n---\n\n'),
    { label: 'grudge-merge', phase: 'Grudge Review' }))
}

async function deadcodeAdjudicate(deadCandidates) {
  return agent(
    GROUND + '\n\nYOUR ROLE — DEAD-CODE FINAL ADJUDICATION. You are the SINGLE final arbiter of the dead-code candidates below; finders only nominate. For each, hunt hard for references the finders missed (other packages, generated code, reflection, build tags, test-only, external/frontend consumers, DI wiring, SQL-by-name, templates); ONE live reference means NOT DEAD; a candidate you cannot prove unreachable defaults to KEEP. EXCEPTION for API-surface census candidates (proto oneof variants / enum values): references from GENERATED marshalling do NOT count as live — these types are always self-referenced by generated code; require a NON-generated, non-test emitter (something that actually constructs/sets the value) or it is DEAD even though it ships as public API. Same false-positive dread and receipts discipline. Output a "## Dead-code adjudication" table (candidate | location | REALLY DEAD? + receipts | REMOVE/KEEP + why | confidence) then a one-line tally.\n\nCANDIDATES:\n' + (deadCandidates || 'none'),
    { label: 'deadcode-adjudicate', phase: 'Grudge Review' })
}

// ---- run ----
// Phase functions (security, deadCodeSweep, grudgeCodeReview) manage their own internal bounding via
// critical() and bounded(). The outer run block uses .catch() only — wrapping a phase function in a
// second bounded() call starts an outer timer that fires before the inner steps complete, discarding
// all completed work (A13). Leaf agent() calls in a fan-out use bounded(); phase functions use .catch().
log('WATCHDOG: arm a harness wake-up per phase — watch for '
  + OUTDIR + '/security-findings.md (~30 min after launch), then '
  + OUTDIR + '/artefact-next.md (~75 min). '
  + 'Distinguish slow-but-alive (transcript events still growing) from genuinely hung before aborting; see SKILL.md NO SILENT HANG.')
const [sec, deadCandidates] = await parallel([
  () => security().catch(e => { log('security phase error: ' + (e && e.message)); return null }),
  () => deadCodeSweep().catch(e => { log('dead-code phase error: ' + (e && e.message)); return null }),
])
const [grudgeCode, deadAdjud] = await parallel([
  () => grudgeCodeReview().catch(e => { log('grudge error: ' + (e && e.message)); return null }),
  () => critical('deadcode-adjudicate', SYNTHESIS_DEADLINE_MS, () => deadcodeAdjudicate(deadCandidates)),
])
const grudgeOut = (grudgeCode || '(grudge code-review step did not complete)') + '\n\n=== DEAD-CODE ADJUDICATION ===\n\n' + (deadAdjud || '(dead-code adjudication step did not complete)')

// Synthesis is split into Planner → Author: reading all inputs AND writing a full document in one
// turn reliably blew the deadline on large artefact + large finding sets. The Planner is read-heavy
// (no writing); the Author is write-heavy (no decisions). Each carries roughly half the context.
// Both steps are critical() — a stalled planner produces nothing for the author to act on.
const changePlan = await critical('synthesise-plan', SYNTHESIS_DEADLINE_MS, () => agent(
  GROUND + '\n\nYOUR ROLE: CHANGE PLANNER — read the artefact and all findings, decide what changes, output a structured plan. Do NOT write artefact-next.md yet.\n\n'
  + 'INPUTS:\n- Security findings:\n' + ((sec && sec.synthesis) || '(none)')
  + '\n\n- Adversarial review + dead-code adjudication:\n' + (grudgeOut || '(none)')
  + '\n\nRULES: CODE WINS (correct stale spec claims); honour PRIORS (do not re-litigate settled decisions).\n\n'
  + 'OUTPUT — three sections, no prose outside them:\n\n'
  + '## Change list\n| id | target section | action (ADD / CORRECT / REMOVE / PRESERVE) | what changes |\n\n'
  + '## ROI pass\nFor every proposed test requirement: | requirement | Gate A (feature built at HEAD? Y/N) | Gate B (behavioural/security value? Y/N) | KEEP or DISCARD + reason |\n\n'
  + '## Open items\nBullet list of items needing a human decision before the next version is final.\n\n'
  + 'Artefact: ' + ARTEFACT + '  Code map: ' + CODEMAP,
  { label: 'synthesise-plan', phase: 'Synthesis' }))

const synth = await critical('synthesise-author', SYNTHESIS_DEADLINE_MS, () => agent(
  GROUND + '\n\nYOUR ROLE: AUTHOR — apply the change plan below mechanically to produce the next artefact version. Make no new decisions; implement exactly what the plan specifies.\n\n'
  + 'CHANGE PLAN:\n' + (changePlan || '(planner did not complete — no artefact can be written; return a clear error)')
  + '\n\nRULES: PRESERVE correct content verbatim with its id; ADD with fresh non-colliding ids + coverage rows; recompute Counts ACCURATELY (requirement bullets == coverage rows; no duplicate ids); no open-questions section in the artefact — open items are in the plan above and belong in your return summary only; append Changelog + Requirements-coverage map + dead-code appendix. House language/style.\n\n'
  + 'Write the COMPLETE next version to ' + OUTDIR + '/artefact-next.md and a concise memo to ' + OUTDIR + '/changeset.md.\n'
  + 'Return ONLY (<250 words): the two output paths; before/after requirement counts; change-class tally; ROI-pass prune count (evaluated N / no-feature E / low-ROI F / kept K); open items verbatim from the plan.\n\n'
  + 'Artefact: ' + ARTEFACT + '  Code map: ' + CODEMAP,
  { label: 'synthesise-author', phase: 'Synthesis' }))

return { securitySynthesis: sec && sec.synthesis, deadCandidates, grudge: grudgeOut, synthSummary: synth }
