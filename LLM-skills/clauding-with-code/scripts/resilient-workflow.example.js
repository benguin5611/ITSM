// resilient-workflow.example.js — ILLUSTRATIVE reference, not run in production.
//
// PACKAGING NOTICE: this canonical file ships in every Claude.ai skill archive,
// injected at build time by `nix build .#skill-zips`. Edit only this root copy;
// it is intentionally not duplicated in source skill directories.
//
// A minimal, project-agnostic workflow showing the orchestration-economy patterns
// (see ../references/orchestration-economy.md) on a runtime that exposes:
//   agent(prompt, opts) -> Promise<string>   one sub-agent call
//   parallel(thunks)    -> Promise<any[]>     run thunks concurrently, await all
//   phase(title)        -> void               mark a pipeline phase (for the UI/log)
//   log(msg)            -> void               structured log line
//   budget              -> {total, spent(), remaining()}  optional token budget
//
// One script, three sizes: pass args.size = 'small' | 'medium' | 'large' (or
// override any knob individually). One file on purpose — three near-identical
// scripts would triplicate the guard machinery and drift apart (the A21 failure).
//
// Sub-agents and the parent skill: a sub-agent must NEVER invoke the
// clauding-with-code orchestrator itself — its checkpoints need the human, and
// orchestration does not nest. What a sub-agent inherits is DOCTRINE: pass the
// reference files relevant to the work as args.doctrine and each writer is told
// to read and follow them.
//
// The pipeline is deliberately tiny — a PLANNER decides a partition, a waved
// WRITER fan-out fills each slice, and a cheap REASSEMBLE stitches the manifest —
// so the guards are the point, not the work. The DEFENCE-IN-DEPTH LADDER, outermost
// first; each layer assumes the ones above it failed:
//
//   L0  git bracket              — read-only-git preamble on every agent; writers
//                                  may write ONLY under the units dir; pre/postflight
//                                  probes (reserved budget) detect drift, loudly,
//                                  even after an abort — never auto-fixed (§10)
//   L1  harness caps + waves     — only ~min(16, cores-2) agents truly run; waves
//                                  of cap-1 mean no deadline ever counts queue time (§2)
//   L2  budget counters          — the agent budget is DERIVED from the plan (the
//                                  human picks a size intent, never invents numbers),
//                                  capped by the preset ceiling, enforced in code
//                                  with a two-tier token floor; drops are logged,
//                                  never silent (§1, A47)
//   L3  fail loud, fail fast     — an agent that DIES (null return / thrown error)
//                                  fails its slice IMMEDIATELY, not at the backstop
//   L4  heartbeat + watchdog     — workers touch a .progress file; a cheap poller
//                                  checks mtimes each cycle and trips a presumed-dead
//                                  worker after 2 stale polls, so a 5-minute death
//                                  never holds its slot for a 1-hour backstop (§4)
//   L5  deadline backstops       — derived from the planner's per-slice estimate
//                                  (2x, preset-capped), escalate 1.5x on retry (§4)
//   L6  artefact-first           — the disk is the durable channel; a timeout on
//                                  RETURN loses nothing (§5, §8, A52)
//   L7  disk-truth verify        — receipts are claims, not facts (A41): one cheap
//                                  probe over every expected unit catches salvage
//                                  (finished, overran on return) AND liars (receipt
//                                  returned, no file) before anything is re-bought
//   L8  targeted tail            — only genuinely missing slices retried, once,
//                                  escalated (§7)
//   L9  triage before attempt 3  — a slice that failed twice is DIAGNOSED, never
//                                  blindly re-run (§6): one batched triage verdict
//                                  (split / rescope / retry / impossible) drives one
//                                  recovery wave; whatever still fails ships as a
//                                  NAMED gap with its diagnosis — no gap unexplained
//   L10 circuit breaker          — a first wave with zero receipts AND zero
//                                  artefacts is systemic: abort before wave two
//   L11 flight recorder          — journal + transcripts archived; resume-from-cache
//                                  re-runs only the failed step (§6, §9)
//   L12 harness wake-up watchdog — OUTSIDE this script: a scheduled re-invocation
//                                  that survives the run itself dying (§4)
//   L13 flagForHuman routing      — a KNOWN-risky Bash op (cd, shell $var expansion, a
//                                  genuinely unlisted binary) is never handed to a background
//                                  sub-agent at all -- there is no retry after that kind of
//                                  interrupt, the agent's turn just ends with zero output.
//                                  Its POSITION in the dependency graph decides the handling
//                                  (see BASH_RULES, §11): a PREREQ is probed (doneWhen) at
//                                  Preflight and every unmet one aborts in one batched
//                                  fail-fast before the planner spends a token — or throws
//                                  immediately if discovered mid-run; only a TERMINAL step
//                                  (gates nothing in this run) defers to PENDING_HUMAN_STEPS
//                                  for the live orchestrator to run directly after the run

export const meta = {
  name: 'resilient-workflow-example',
  description: 'illustrative resilient fan-out with small/medium/large presets: git-bracketed, budgeted, estimate-aware waved artefact-first writers with heartbeat watchdog, disk-truth verify, targeted tail, triage-guided recovery, reassemble from disk',
  phases: [
    { title: 'Preflight' },
    { title: 'Plan' },
    { title: 'Write' },
    { title: 'Verify' },
    { title: 'Tail' },
    { title: 'Recover' },
    { title: 'Reassemble' },
    { title: 'Postflight' },
  ],
}

// ---- size presets ------------------------------------------------------------
// waveSize is deliberately cap-1 (~9): the watchdog's checker agent needs a free
// concurrency slot, or it queues behind the very wave it is meant to watch.
// 'small' skips the watchdog — with a handful of short-deadline agents the
// backstop alone is proportionate. 'large' assumes the human has BOTH agreed the
// budget and raised the session workflow-size guideline (default ~15) to match.
// writeMs is the HARD CAP on any one writer's deadline; the actual per-slice
// deadline is derived from the planner's estimate (see msFor).
const PRESETS = {
  small:  { agentBudget: 12,  waveSize: 6, writeMs: 8  * 60 * 1000, watchdog: false },
  medium: { agentBudget: 30,  waveSize: 9, writeMs: 10 * 60 * 1000, watchdog: true },
  large:  { agentBudget: 100, waveSize: 9, writeMs: 12 * 60 * 1000, watchdog: true },
}

// Agents (and some invocation paths) hand back JSON wrapped in markdown fences
// or as a JSON-encoded string — both hit a live E2E run. Strip one outer fence,
// then parse; undefined means unparseable (callers log their own message).
function parseJsonLoose(raw) {
  if (typeof raw !== 'string') return undefined
  let s = raw.trim()
  const m = s.match(/^```[a-zA-Z]*\s*([\s\S]*?)\s*```$/)
  if (m) s = m[1].trim()
  try { return JSON.parse(s) } catch (e) { return undefined }
}

// ---- config (keep inputs in args so a resume re-passes them; §6). ------------
// args can arrive as a JSON-encoded STRING (the harness warns about stringified
// args; a live E2E hit it and every knob silently fell back to its default,
// retargeting the run at the wrong directory) — tolerate both shapes.
const A = (typeof args === 'string' ? parseJsonLoose(args) : args) || {}
const SIZE = PRESETS[A.size] ? A.size : 'medium'
const P = PRESETS[SIZE]
const REPO = A.repo || '.'
// outDir is REQUIRED, no default: defaulting to '.' made a live E2E litter the
// repo working tree with units/ and manifest.md. Fail closed, loudly, before
// any agent spends a token.
if (!A.outDir) throw new Error('FAIL-FAST: args.outDir is required — refusing to default to "." and write units/ + manifest.md into the current directory (usually the repo). Pass an explicit output directory.')
const OUTDIR = A.outDir
const UNITS_DIR = OUTDIR + '/units' // artefact-first: every writer owns one file here
const DOCTRINE = Array.isArray(A.doctrine) ? A.doctrine : [] // reference files each writer must follow
// Agent budget: the human picks the SIZE INTENT (preset); the NUMBER is derived
// from the plan after the planner runs — humans have no frame of reference for
// agent/token counts and reliably underestimate, so never ask them to invent one.
// The preset ceiling is the hard safety cap; an explicit args.agentBudget (used
// by tests and power users) skips auto-derivation.
const BUDGET_CEILING = P.agentBudget
const BUDGET_EXPLICIT = !!A.agentBudget
let AGENT_BUDGET = A.agentBudget || BUDGET_CEILING
const WAVE_SIZE = A.waveSize || P.waveSize
const WRITE_MS = A.writeMs || P.writeMs
const WATCHDOG = (A.watchdog !== undefined) ? !!A.watchdog : P.watchdog
const PLAN_MS  = A.planMs  || 8 * 60 * 1000 // planner: small, but a single point of failure
const STITCH_MS = A.stitchMs || 6 * 60 * 1000 // reassembly/verify: cheap, still bounded
const ESCALATE = 1.5 // retry deadline multiplier: one trip may just mean the estimate was wrong
const POLL_MS = A.pollMs || 4 * 60 * 1000 // watchdog cycle; presumed-dead after 2 stale polls
const STRIKES = 2
const WATCH_BUDGET = A.watchBudget || Math.max(6, Math.ceil(AGENT_BUDGET / 3)) // poller can't starve workers
const GIT_PROBES = 2 // reserved, OUTSIDE the agent budget: git safety must survive budget exhaustion
// Two-tier token floor: the human sets the turn's token target (a "+500k"-style
// directive — budget.total is null when they didn't); the harness enforces it as
// a HARD ceiling (agent() throws past it). These floors are OUR softer brake:
// workers stop early enough to leave room for the verify/stitch tail, and the
// cheap critical steps (verify, salvage, reassemble) run closer to the wire so a
// budget-squeezed run still ends coherent instead of dying mid-wave.
const TOKEN_FLOOR = A.tokenFloor || 40000
const TOKEN_FLOOR_CRITICAL = A.tokenFloorCritical || 12000
// Model routing per slice tier. The trust boundary is deliberate: haiku is
// trusted ONLY for small documentation-only updates ("docs-small", est <= the
// max below) — a slice that claims docs-small but estimates bigger is DEMOTED to
// mechanical, loudly. Mechanical work routes to a mid tier at low effort;
// judgement inherits the session model (omit — the inherit-unless-confident rule).
const ROUTING = Object.assign({ docsSmall: 'haiku', mechanical: 'sonnet', judgement: null }, A.routing || {})
const DOCS_SMALL_MAX_MIN = A.docsSmallMaxMinutes || 10
const modelFor = s => (s.tier === 'docs-small' ? ROUTING.docsSmall : s.tier === 'mechanical' ? ROUTING.mechanical : ROUTING.judgement) || undefined

const tokenNote = () => (typeof budget !== 'undefined' && budget.total)
  ? ' tokens=' + budget.spent() + '/' + budget.total : ''

log('preset=' + SIZE + ' budget=' + AGENT_BUDGET + ' wave=' + WAVE_SIZE + ' writeMs=' + WRITE_MS + ' watchdog=' + WATCHDOG + tokenNote())
if (SIZE === 'large') log('LARGE preset: confirm the human agreed ' + AGENT_BUDGET + ' agents AND raised the session workflow-size guideline (default ~15) before launch — otherwise the plan gets silently reshaped')

// ---- per-agent preamble: token thrift + git safety, on EVERY sub-agent. --------
// Sub-agents do not inherit the orchestrator's thrift or its git discipline.
// caveman and ponytail ship as PLUGINS that expose skills/commands — a sub-agent
// may or may not see them — so the preamble invokes them when visible and bakes
// their essence in as the fallback either way. The git rules are NON-NEGOTIABLE:
// this workflow's agents observe the repo, they never mutate it. A variant whose
// writers genuinely must edit repo files runs each writer in its own worktree
// (isolation: 'worktree') and still never touches branches — see
// parallel-agents.md for multi-agent-on-one-repo discipline.
const STYLE = 'Before anything else: if a `caveman` skill or command is available (it ships via a plugin), invoke it '
  + 'with args "ultra" (terse output); if a `ponytail` skill or command is available, invoke it (minimal code). '
  + 'If either is missing, continue without it — never fail or spend words on its absence. Work in their spirit '
  + 'regardless: terse output, zero filler; minimal code, no speculative abstraction.\n'
const GIT_RULES = 'Git safety (non-negotiable): run NO git command that changes state — no commit, push, pull, '
  + 'checkout/switch, reset, rebase, merge, clean, stash, branch create/delete, tag, or worktree add/remove — and '
  + 'never touch the .git directory. Read-only git (status, log, diff, show, rev-parse) is fine.\n\n'
// A background agent's Bash call has nobody to answer a permission prompt. Most calls succeed
// fine even off-allowlist, but a `cd` (standalone or `(cd X && Y)`) or a shell variable
// assignment+expansion (`R=x; cmd $R`) ALWAYS stalls waiting for approval that never comes,
// regardless of what's allowlisted — both are blanket policy exclusions an allowlist entry can't
// fix. A genuinely unlisted binary (arbitrary generated scripts, `git worktree add`) also stalls
// with no prompt-side fix — route it to a human-run step outside the fan-out (flagForHuman,
// below), or add a narrowly-scoped allowlist entry, rather than asking a background agent to
// attempt it.
const BASH_RULES = 'Bash discipline (this session is unattended in the background — nobody can answer a permission '
  + 'prompt): NEVER use `cd` as a standalone command or in a `(cd X && Y)` subshell — always pass absolute paths '
  + 'directly to the tool/command instead. NEVER use a shell variable assignment + expansion in a Bash command '
  + '(e.g. `R=/x; cmd $R`) — inline the literal absolute path every time instead, even if it repeats. Both patterns '
  + 'always stall waiting for approval that will never come, no matter what is allowlisted. Prefer the Grep/Edit/'
  + 'Read/Write tools over Bash entirely for anything they can do (searching text, editing files, moving/renaming a '
  + 'tracked file via Edit+Write rather than a shell `mv` where avoidable) — reserve Bash for the few things that '
  + 'genuinely need a shell.\n\n'
const PREAMBLE = STYLE + GIT_RULES + BASH_RULES

// ---- spawn: the budgets are enforced in code (§1). ----------------------------
// Past a cap, spawn refuses and logs exactly what was dropped — a silent cap
// reads as coverage (A47). opts.reserveCritical routes a spawn to the deeper
// token floor (verify/salvage/stitch). The watchdog's checkers and the git
// probes draw on their own small reserves so neither can starve (or be starved
// by) the workers.
let spawned = 0
let watchSpawned = 0
let gitSpawned = 0
const dropped = []
// ---- flagForHuman: some Bash operations are NEVER safe to hand a background sub-agent —
// a stall on `cd`, shell $var expansion, or a genuinely unlisted binary (arbitrary generated-
// script execution, `mv`/`cp` of a tracked repo file, `git worktree add/remove`, anything a
// managed-settings allowlist doesn't cover) means the agent's turn ends immediately with ZERO
// output — no receipt, nothing to recover from disk — so there is no retry, tail, or triage that
// fixes this; the agent never gets a chance to run again after the interrupt. The fix is
// upstream of the fan-out:
// KNOWN-risky ops (identified when the script is authored, not discovered at runtime) are never
// spawned as a sub-agent prompt at all. Call flagForHuman() instead and skip the agent() call —
// the exact command is collected and returned to the ORCHESTRATOR (the live, foreground session
// that invoked this workflow), who can get it approved for real or run it directly. This is not
// a bug-recovery path — it is a plan-time routing decision, same status as choosing which slice
// runs on which model tier.
//
// A human step's handling is decided by its POSITION in the dependency graph, never by the
// clock (orchestration-economy.md §11):
//   prereq   — something in this run reads its output. Declared before the pipeline starts,
//              probed at Preflight via its doneWhen check; every unmet prereq aborts the run
//              in ONE batched fail-fast BEFORE the planner spends a token. The human runs the
//              batch live (prompts answered for real), resumes from cache, the probe passes.
//              Discovered mid-run instead: flagForHuman throws immediately — spending the
//              remaining budget on work that assumes the step happened is the worst outcome.
//   terminal — nothing in this run reads its output (a push, a publish, a final verify).
//              Deferred to PENDING_HUMAN_STEPS and returned in the result — the only class
//              where deferral is correct.
// position defaults to 'prereq' — fail closed: a terminal step mistagged prereq costs one loud
// early stop; a prereq mistagged terminal ships a whole run built on a step that never happened.
// By construction, pendingHumanSteps in a COMPLETED result are all terminal.
const PENDING_HUMAN_STEPS = []
let prereqGateDone = false
function flagForHuman(label, exactCommand, reason, opts) {
  const o = opts || {}
  const position = o.position === 'terminal' ? 'terminal' : 'prereq'
  if (position === 'prereq' && !o.doneWhen) {
    throw new Error('FAIL-FAST: flagForHuman("' + label + '") is position=prereq but has no doneWhen probe — '
      + 'an unverifiable prerequisite would abort every resume, even after the human has done it. Give it a '
      + 'mechanical doneWhen check (e.g. "file /abs/path exists"), or tag it position:"terminal" if nothing '
      + 'in this run reads its output.')
  }
  if (position === 'prereq' && prereqGateDone) {
    throw new Error('FAIL-FAST: prerequisite human step "' + label + '" discovered MID-RUN (' + exactCommand + ') — '
      + reason + '. Continuing would spend the remaining budget on work that assumes it happened. Run it live in '
      + 'the foreground, promote this flag to the top of the script so its doneWhen probe gates the next run, '
      + 'then resume from cache — completed steps replay free.')
  }
  PENDING_HUMAN_STEPS.push({ label, command: exactCommand, reason, position, doneWhen: o.doneWhen })
  log((position === 'prereq' ? 'HUMAN-PREREQ' : 'HUMAN-STEP-REQUIRED') + ': "' + label + '" — ' + reason
    + '. A background agent cannot get this approved; the orchestrator must run it directly: ' + exactCommand)
}
function spawn(prompt, opts) {
  const label = (opts && opts.label) || 'unlabelled'
  if (spawned >= AGENT_BUDGET) {
    dropped.push(label)
    log('BUDGET: agent cap ' + AGENT_BUDGET + ' reached — dropped "' + label + '"')
    return Promise.resolve(null)
  }
  const floor = (opts && opts.reserveCritical) ? TOKEN_FLOOR_CRITICAL : TOKEN_FLOOR
  if (typeof budget !== 'undefined' && budget.total && budget.remaining() < floor) {
    dropped.push(label)
    log('BUDGET: token budget nearly spent (' + budget.remaining() + ' < floor ' + floor + ') — dropped "' + label + '"')
    return Promise.resolve(null)
  }
  spawned++
  const o = Object.assign({}, opts)
  delete o.reserveCritical
  return agent(PREAMBLE + prompt, o)
}
function spawnWatch(prompt, opts) {
  if (watchSpawned >= WATCH_BUDGET) {
    log('WATCHDOG: own budget spent (' + WATCH_BUDGET + ') — polling stops; deadline backstops remain armed')
    return Promise.resolve(null)
  }
  watchSpawned++
  return agent(PREAMBLE + prompt, opts).catch(e => { log('watchdog checker failed: ' + (e && e.message)); return null })
}
function spawnGit(prompt, opts) {
  if (gitSpawned >= GIT_PROBES) return Promise.resolve(null)
  gitSpawned++
  return agent(PREAMBLE + prompt, opts).catch(e => { log('git probe failed: ' + (e && e.message)); return null })
}

// ---- withDeadline: bound any promise. -----------------------------------------
// GENEROUS backstops, not the stall detector — the watchdog below finds death
// early; the backstop only converts a true undetected hang into a loud abort.
// If the sandbox has no timers, degrade — but say so LOUDLY. No Date.now anywhere
// — we race against a timer, we do not poll a clock (§4).
const HAS_TIMERS = typeof setTimeout === 'function'
if (!HAS_TIMERS) log('WARNING: no timers in this sandbox — deadline bounding AND the watchdog are OFF; rely on the harness wake-up')
function withDeadline(p, ms, label) {
  if (!HAS_TIMERS) return Promise.resolve(p)
  let t
  const timeout = new Promise((_, rej) => {
    t = setTimeout(() => rej(new Error('DEADLINE: "' + label + '" exceeded ' + ms + 'ms')), ms)
  })
  return Promise.race([
    Promise.resolve(p).then(v => { clearTimeout(t); return v }, e => { clearTimeout(t); throw e }),
    timeout,
  ])
}
// Interruptible sleep. The losing timer MUST be cleared: a race abandons its
// loser still scheduled, and a leaked ref'd timer (up to a full poll interval)
// outlives the wave and delays run teardown.
function sleep(ms, stop) {
  if (!HAS_TIMERS) return Promise.resolve()
  let t
  return Promise.race([new Promise(r => { t = setTimeout(r, ms) }), stop.p])
    .then(() => clearTimeout(t))
}

// ---- critical: guard a sequential single-point-of-failure step. ---------------
// Bound it, retry ONCE with an ESCALATED deadline (transient flakes and wrong
// estimates both happen), then abort LOUDLY with a resume hint — never hang
// silently. A loud abort is NOT proof the work wasn't done: inspect the artefact
// on disk first (§5), then read the run journal for what each agent actually
// returned (§9), diagnose, re-pass args verbatim, THEN resume from cache (§6).
async function critical(label, ms, makeCall) {
  for (let attempt = 1; attempt <= 2; attempt++) {
    const deadline = attempt === 1 ? ms : Math.round(ms * ESCALATE)
    try { return await withDeadline(makeCall(), deadline, label) }
    catch (e) {
      log('CRITICAL "' + label + '" attempt ' + attempt + '/2 failed (' + deadline + 'ms): ' + (e && e.message))
      if (attempt === 2) {
        throw new Error('FAIL-FAST: critical step "' + label + '" stalled/failed twice. '
          + 'Before resuming: (1) check whether its output already exists on disk; (2) read the run journal for '
          + 'what it actually returned; (3) diagnose (bound or split the step), never resume blindly into the '
          + 'same hang; (4) re-pass args verbatim. Then resume from cache so only this step re-runs.')
      }
    }
  }
}

// ---- tripwire: lets the watchdog stop the wait on a presumed-dead worker. -----
// The script CANNOT kill an in-flight agent — it can only stop waiting for it
// (the harness frees the slot when the agent actually ends). Tripping converts
// "timer says 1h+ but it died at minute 5" into a loud drop within ~2 polls; the
// verify/tail layers then recover the slice.
function tripwire(label) {
  let trip
  const promise = new Promise((_, rej) => {
    trip = (why) => rej(new Error('PRESUMED-DEAD: "' + label + '" — ' + why))
  })
  return { promise, trip }
}
function makeStop() {
  let fire
  const p = new Promise(r => { fire = r })
  return { done: false, p, fire }
}

// ---- watchdog: progress-based liveness, polled DURING each wave (§4). ---------
// Judges by heartbeat mtime, never by elapsed time. Each writer touches its own
// <key>.progress file as it works; a cheap low-effort checker reads the ages. A
// worker with no fresh writes across 2 consecutive polls is presumed dead and its
// tripwire fires. This finds the hang long before the backstop would — the
// backstop stays only for what the poller can't see (checker budget spent, no
// timers, a worker that heartbeats but never finishes).
async function watchdog(waveSlices, wires, settled, stop, phaseName) {
  const strikes = {}
  for (const s of waveSlices) strikes[s.key] = 0
  while (HAS_TIMERS) {
    await sleep(POLL_MS, stop)
    if (stop.done) return
    const open = waveSlices.filter(s => !settled.has(s.key))
    if (!open.length) return
    const raw = await spawnWatch(
      'Mechanical liveness check — no analysis, no fixing. For each key in [' + open.map(s => s.key).join(', ') + '], '
      + 'find the MOST RECENTLY modified of ' + UNITS_DIR + '/<key>.progress and ' + UNITS_DIR + '/<key>.md and report '
      + 'the whole seconds since that modification, or null if neither file exists. '
      + 'Return STRICT JSON: {"<key>": <seconds or null>, ...} — nothing else.',
      { label: 'watchdog:poll', phase: phaseName, agentType: 'Explore', effort: 'low' })
    if (stop.done) return
    if (raw === null) return // checker budget spent or checker died — backstops still armed
    const ages = parseJsonLoose(raw)
    if (ages === undefined || ages === null || typeof ages !== 'object') { log('watchdog: non-JSON report — skipping this cycle'); continue }
    const staleAfter = Math.round(POLL_MS / 1000) + 60 // fresh = written within roughly one poll cycle
    for (const s of open) {
      if (settled.has(s.key)) continue
      const age = ages[s.key]
      if (typeof age === 'number' && age <= staleAfter) { strikes[s.key] = 0; continue }
      strikes[s.key]++
      log('watchdog: "' + s.key + '" ' + (age == null ? 'no heartbeat yet' : age + 's since last write')
        + ' — strike ' + strikes[s.key] + '/' + STRIKES)
      if (strikes[s.key] >= STRIKES) {
        wires.get(s.key).trip('no artefact/heartbeat progress across ' + STRIKES + ' polls (~'
          + Math.round(STRIKES * POLL_MS / 60000) + ' min); stopped waiting instead of burning the backstop')
      }
    }
  }
}

// ---- runWatchedWave: one wave, every guard wired in. ---------------------------
// Each worker races THREE ways to fail fast and loud, in detection order:
//   died     — agent() returned null (terminal error / budget drop): fails the
//              slice IMMEDIATELY, zero seconds of timer theatre
//   presumed — the watchdog tripped it after 2 stale polls (~8 min)
//   deadline — the estimate-derived backstop, last resort only
// Model economy is routed per slice from the planner's tier tag (state the
// choice, make it auditable — token-and-cost-economy.md): docs-small -> haiku at
// low effort (the ONLY haiku-trusted work: small documentation updates),
// mechanical -> mid tier at low effort, judgement -> inherit the session model.
// A failed worker degrades to null (the verify/tail layers own recovery); the
// wave itself never wedges.
async function runWatchedWave(waveSlices, msOf, phaseName, prefix, promptOf) {
  const wires = new Map(waveSlices.map(s => [s.key, tripwire(prefix + s.key)]))
  const settled = new Set()
  const stop = makeStop()
  const waveP = parallel(waveSlices.map(s => () =>
    withDeadline(
      Promise.race([
        spawn(promptOf(s), {
          label: prefix + s.key,
          phase: phaseName,
          effort: (s.tier === 'mechanical' || s.tier === 'docs-small') ? 'low' : undefined,
          model: modelFor(s),
        }).then(r => {
          if (r === null) throw new Error('AGENT-DIED: "' + prefix + s.key + '" returned null (terminal error or budget drop) — failing fast, not waiting out the deadline')
          return r
        }),
        wires.get(s.key).promise,
      ]), msOf(s), prefix + s.key)
      .then(
        r => { settled.add(s.key); return r },
        e => { settled.add(s.key)
          log('LOUD-DROP "' + prefix + s.key + '": ' + (e && e.message)
            + ' — if this slice used Bash, a silent unattended stall (cd, shell $var expansion, or a genuinely '
            + 'unlisted binary — see BASH_RULES above) is a common cause; consider PENDING_HUMAN_STEPS or a manual rerun')
          return null })
  ))
  const wdP = WATCHDOG
    ? watchdog(waveSlices, wires, settled, stop, phaseName).catch(e => log('watchdog crashed (non-fatal, backstops remain): ' + (e && e.message)))
    : null
  const results = await waveP
  stop.done = true
  stop.fire()
  if (wdP) await wdP
  return results
}

// ---- diskCheck: which expected units actually exist? ---------------------------
// Three-valued on purpose: an array is the truth from disk; null means the probe
// itself failed (budget-dropped or died), and the caller must FALL BACK to
// receipts rather than treat "probe failed" as "nothing on disk" — otherwise a
// budget-squeezed run would declare every finished unit missing (A47's shape).
async function diskCheck(keys, phaseName) {
  const raw = await critical('salvage-check', STITCH_MS, () => spawn(
    'Mechanical check only. List which of these files exist AND are non-empty under ' + UNITS_DIR + ': '
    + keys.map(k => k + '.md').join(', ') + '. Return STRICT JSON: an array of the slice keys '
    + '(without .md) whose file exists and is non-empty — nothing else.',
    { label: 'salvage-check', phase: phaseName, agentType: 'Explore', effort: 'low', reserveCritical: true }))
  if (raw === null) { log('disk check returned nothing (dropped or died) — caller falls back to receipts') ; return null }
  const v = parseJsonLoose(raw)
  if (Array.isArray(v)) return v
  log('disk check did not return a JSON array — caller falls back to receipts')
  return null
}

// ---- git probes: bracket the run so no agent can silently wreck the repo. ------
// Reserved budget (spawnGit) so the POSTFLIGHT runs even when the agent budget is
// exhausted or the run aborted. Drift is REPORTED, loudly, never auto-fixed — the
// human disposes. Dirty-count changes are informational (the units dir may live
// inside the repo); branch/stash/worktree changes are hard drift.
const GIT_PROBE_PROMPT = 'Mechanical git check — read-only, no analysis, no fixing. Run exactly these, so the '
  + 'probe cannot drift to some other repo you can see: git -C ' + REPO + ' rev-parse --abbrev-ref HEAD; '
  + 'git -C ' + REPO + ' status --porcelain; git -C ' + REPO + ' stash list; git -C ' + REPO + ' worktree list. '
  + 'Return STRICT JSON, bare, no code fences: '
  + '{"branch":"<name>","dirty":<porcelain line count>,"stashes":<count>,"worktrees":<count>} — nothing else. '
  + 'If ' + REPO + ' is not a git repository, return {"branch":null,"dirty":0,"stashes":0,"worktrees":0}.'
function gitParse(raw, label) {
  if (raw === null) { log('GIT: ' + label + ' probe returned nothing — repo state UNVERIFIED, check it by hand'); return null }
  const v = parseJsonLoose(raw)
  if (v && typeof v === 'object' && !Array.isArray(v)) return v
  log('GIT: ' + label + ' probe returned non-JSON — repo state UNVERIFIED')
  return null
}

// ---- pipeline -------------------------------------------------------------------

// 0) GIT PREFLIGHT: record the repo state the run started from.
phase('Preflight')
const gitBase = gitParse(await spawnGit(GIT_PROBE_PROMPT, { label: 'git:preflight', phase: 'Preflight', agentType: 'Explore', effort: 'low' }), 'preflight')
if (gitBase) log('git preflight: branch=' + gitBase.branch + ' dirty=' + gitBase.dirty + ' stashes=' + gitBase.stashes + ' worktrees=' + gitBase.worktrees)

let slices = []
let missing = []
let manifest = null
let fatal = null
let expectedKeys = []
const gapReasons = {}
const receiptByKey = {}

try {
  // Demo calls, opt-in only (args.demo*) — show flagForHuman's real shapes without changing
  // this pipeline's default behaviour. A real script declares its human steps here, at the
  // top, and skips the doomed agent() call at the point the op would otherwise have run.
  if (A.demoFlagForHuman) {
    flagForHuman('demo-risky-op', 'mv ' + REPO + '/tools/old.py ' + REPO + '/tools/new.py',
      'plain filesystem rename — not on any Bash allowlist, a background agent attempting it stalls with zero output',
      { position: 'terminal' })
  }
  if (A.demoPrereqFlag) {
    flagForHuman('demo-prereq', 'mv ' + REPO + '/tools/old.py ' + REPO + '/tools/new.py',
      'rename the run depends on — every slice reads the new path',
      { doneWhen: 'file ' + REPO + '/tools/new.py exists' })
  }
  if (A.demoPrereqNoProbe) {
    flagForHuman('demo-unverifiable-prereq', 'mv ' + REPO + '/tools/old.py ' + REPO + '/tools/new.py', 'prereq with no probe')
  }

  // 0b) PREREQ GATE: probe every declared prerequisite human step ONCE, batched, BEFORE the
  // planner spends a token. A satisfied prereq is done — dropped from the pending list. Any
  // unmet prereq fails the whole batch loudly so the human runs them live in ONE interaction
  // and resumes from cache. A probe that returns nothing or non-JSON fails CLOSED — an
  // unverifiable prerequisite is an unmet one.
  // E2E-found: a resumed run replays CACHED agent results for identical prompts, and a probe of
  // external state must never be cache-replayed — the whole point of resuming is that the human
  // just changed the world. args.prereqAttempt is the cache-buster: bumping it re-runs the probe
  // (and only the probe); every other cached step still replays free.
  const prereqs = PENDING_HUMAN_STEPS.filter(s => s.position === 'prereq')
  if (prereqs.length) {
    const rawProbe = await critical('prereq-check', STITCH_MS, () => spawn(
      'Mechanical check only — no analysis, no fixing. [prereq attempt ' + (A.prereqAttempt || 1) + '] '
      + 'For each item report whether its condition is ALREADY '
      + 'true right now: ' + prereqs.map(s => '"' + s.label + '": ' + s.doneWhen).join('; ') + '. '
      + 'Return STRICT JSON: {"<label>": true|false, ...} — nothing else.',
      { label: 'prereq-check', phase: 'Preflight', agentType: 'Explore', effort: 'low', reserveCritical: true }))
    const probed = parseJsonLoose(rawProbe)
    const probeOk = probed !== undefined && probed !== null && typeof probed === 'object' && !Array.isArray(probed)
    if (!probeOk) log('prereq probe returned nothing/non-JSON — failing closed, treating every prerequisite as unmet')
    const unmet = probeOk ? prereqs.filter(s => probed[s.label] !== true) : prereqs
    for (const s of prereqs) {
      if (unmet.includes(s)) continue
      log('prereq satisfied: "' + s.label + '" (' + s.doneWhen + ')')
      PENDING_HUMAN_STEPS.splice(PENDING_HUMAN_STEPS.indexOf(s), 1)
    }
    if (unmet.length) {
      throw new Error('FAIL-FAST: ' + unmet.length + ' human prerequisite step(s) unmet — run these live in the '
        + 'foreground (one batch, approval prompts answered for real), then resume from cache with the SAME args '
        + 'plus prereqAttempt: ' + ((A.prereqAttempt || 1) + 1) + ' — the bump forces the probe (and only the '
        + 'probe) to re-read the world instead of replaying its cached verdict: '
        + unmet.map(s => '[' + s.label + '] ' + s.command + ' — ' + s.reason).join('; '))
    }
  }
  prereqGateDone = true

  // 1) PLANNER (critical): reads only COMPACT summaries and decides the partition
  // of work — never a read-all/write-all monolith (§3). Single point of failure,
  // so it is guarded by critical(). It also carries the economy levers: batch tiny
  // units into one slice, estimate each slice, and tag its tier for model routing.
  phase('Plan')
  const planJson = await critical('plan', PLAN_MS, () => spawn(
    'You are the PLANNER. Work ONLY with what is under ' + REPO + ' — do not read, survey, or plan work for '
    + 'anything outside that directory, whatever else you can see. Read only the high-level summaries there '
    + '(do NOT open every file). '
    + 'Decide how to PARTITION the work into independent slices a writer can each own in isolation. '
    + 'BATCH small related units into one slice — one agent per unit of work, never one agent per tiny artefact. '
    + 'Size each slice so one agent finishes it comfortably inside ' + Math.round(WRITE_MS / 2 / 60000) + ' minutes. '
    + 'Return STRICT JSON: an array of {"key","brief","estMinutes","tier"} where estMinutes is your honest '
    + 'single-agent completion estimate and tier is one of: "docs-small" (a SMALL documentation-only update, '
    + 'under ~' + DOCS_SMALL_MAX_MIN + ' minutes, touching prose/markdown only), "mechanical" (deterministic '
    + 'transcription/reconciliation a gate would catch), or "judgement" (design, security, arbitration). '
    + 'Return the JSON BARE — no markdown code fences, no prose, nothing else.',
    { label: 'plan', phase: 'Plan', agentType: 'Explore' }))

  // Beware JSON.parse(null): it parses to null WITHOUT throwing, so a budget-dropped
  // or dead planner (null return) must be guarded explicitly or slices.length crashes.
  const parsedPlan = parseJsonLoose(planJson)
  if (parsedPlan === undefined && planJson !== null) log('planner did not return JSON')
  if (parsedPlan !== undefined && !Array.isArray(parsedPlan)) log('planner returned non-array output')
  slices = Array.isArray(parsedPlan) ? parsedPlan : []
  slices = slices.map(s => {
    const est = (typeof s.estMinutes === 'number' && s.estMinutes > 0) ? s.estMinutes : Math.round(WRITE_MS / 2 / 60000)
    let tier = (s.tier === 'mechanical' || s.tier === 'docs-small') ? s.tier : 'judgement'
    if (tier === 'docs-small' && est > DOCS_SMALL_MAX_MIN) {
      log('routing: "' + s.key + '" claimed docs-small but estimates ' + est + ' min (> ' + DOCS_SMALL_MAX_MIN + ') — DEMOTED to mechanical; haiku is trusted only for small doc updates')
      tier = 'mechanical'
    }
    return { key: s.key, brief: s.brief, estMinutes: est, tier }
  })
  expectedKeys = slices.map(s => s.key)
  log('planner produced ' + slices.length + ' slices')

  // Budget is an OUTPUT of planning, not a human guess: one attempt per slice,
  // a retry/recovery allowance, and fixed overhead (verifies, triage, stitch).
  // The preset ceiling stays the hard cap — if the plan needs more, say so
  // loudly up front instead of silently dropping the tail later.
  if (!BUDGET_EXPLICIT) {
    const derived = Math.ceil(slices.length * 1.6) + 8
    if (derived <= BUDGET_CEILING) {
      AGENT_BUDGET = derived
      log('agent budget auto-derived from the plan: ' + derived + ' (ceiling ' + BUDGET_CEILING + ')')
    } else {
      log('agent budget derived ' + derived + ' EXCEEDS the ' + SIZE + ' preset ceiling ' + BUDGET_CEILING
        + ' — capped at the ceiling; drops will be logged loudly. Prefer a larger size preset or more batching in the plan.')
    }
    log('cost frame (rough, for the human): ~' + AGENT_BUDGET + ' agents max; typical output-token spend '
      + Math.round(AGENT_BUDGET * 10) + 'k-' + Math.round(AGENT_BUDGET * 40) + 'k; actuals logged per wave and in the journal')
  }
  // Zero slices means the whole run would "succeed" doing nothing — fail LOUDLY. (Or
  // use the agent() schema option, which validates structured output at the tool
  // layer and removes this failure mode.)
  if (!slices.length) throw new Error('FAIL-FAST: planner returned no usable slices — nothing to write; fix the planner prompt/output before resuming')

  // ETA: waves run sequentially, agents in a wave run together, so the run estimate
  // is the sum over waves of each wave's slowest slice. Estimates are the planner's,
  // logged as estimates — the journal and the harness UI carry the actuals.
  let runEta = 0
  const waveEta = []
  for (let i = 0; i < slices.length; i += WAVE_SIZE) {
    const eta = Math.max.apply(null, slices.slice(i, i + WAVE_SIZE).map(s => s.estMinutes))
    waveEta.push(eta)
    runEta += eta
  }
  log('ETA (planner estimates): ~' + runEta + ' min across ' + waveEta.length + ' wave(s); per-slice deadlines = 2x estimate, capped at ' + Math.round(WRITE_MS / 60000) + ' min')

  // Deadline per slice: 2x the honest estimate (room to be wrong), floored so a
  // tiny estimate can't produce a hair-trigger, capped by the preset. A slice whose
  // honest estimate busts the cap is a decomposition problem, not a deadline one (§3).
  const msFor = s => Math.min(WRITE_MS, Math.max(3 * 60 * 1000, s.estMinutes * 2 * 60 * 1000))

  // 2) WRITERS (waved, heartbeat-emitting, ARTEFACT-FIRST): one worker per slice.
  // Each writes its unit to its OWN file on disk and returns only a receipt — the
  // disk is the durable channel (§8). Writers may write ONLY under the units dir;
  // doctrine files (args.doctrine) bind them to the parent skill's standards
  // without nesting the orchestrator itself.
  const writerPrompt = (s) =>
    'You are ONE writer. FIRST create ' + UNITS_DIR + '/' + s.key + '.progress and overwrite it with a one-line '
    + 'status every few minutes as you work — it is your heartbeat; a watchdog reads its modification time. '
    + (DOCTRINE.length ? 'Read and follow these doctrine files before writing: ' + DOCTRINE.join(', ') + '. ' : '')
    + 'Read ONLY your slice (' + s.brief + ') under ' + REPO + '. Estimated size: ~' + s.estMinutes + ' min — if you '
    + 'discover it is far bigger, write what you have and say so in your receipt rather than overrunning. '
    + 'WRITE your complete, self-contained unit to ' + UNITS_DIR + '/' + s.key + '.md — the file is the deliverable. '
    + 'Your ONLY writable paths are ' + UNITS_DIR + '/' + s.key + '.md and ' + UNITS_DIR + '/' + s.key + '.progress; '
    + 'modify nothing else, no repository files. Return ONLY a receipt: the file path and a one-line tally.'

  phase('Write')
  // Demo, opt-in: a prerequisite DISCOVERED mid-run (the plan didn't predict it). flagForHuman
  // throws here — front-loading is no longer possible, and the budget must not be spent on
  // work that assumes the step happened. Human runs it live, promotes the flag, resumes.
  if (A.demoMidRunPrereq) {
    flagForHuman('demo-midrun-prereq', 'git -C ' + REPO + ' worktree add ../scratch-worktree',
      'a real git mutation discovered mid-run — correctly gated, undelegatable',
      { doneWhen: 'directory ' + REPO + '/../scratch-worktree exists' })
  }
  for (let i = 0; i < slices.length; i += WAVE_SIZE) {
    const wave = slices.slice(i, i + WAVE_SIZE)
    log('wave ' + (i / WAVE_SIZE + 1) + '/' + waveEta.length + ': ' + wave.length + ' writers, ETA ~' + waveEta[i / WAVE_SIZE] + ' min (+1 slot reserved for the watchdog)' + tokenNote())
    const results = await runWatchedWave(wave, msFor, 'Write', 'write:', writerPrompt)
    wave.forEach((s, j) => { receiptByKey[s.key] = results[j] })
    // CIRCUIT BREAKER: a first wave with zero receipts is either bad luck or a
    // systemic failure (broken prompt, dead model, wrong paths). The disk decides:
    // zero artefacts too -> abort NOW, before burning the remaining waves.
    if (i === 0 && !results.some(Boolean)) {
      const onDisk = (await diskCheck(wave.map(s => s.key), 'Write')) || []
      if (!onDisk.length) {
        throw new Error('FAIL-FAST: first wave produced zero receipts AND zero artefacts on disk — systemic failure, '
          + 'aborting before spending ' + (slices.length - wave.length) + ' more slices. Read the journal, diagnose, resume from cache.')
      }
      onDisk.forEach(k => { receiptByKey[k] = 'salvaged:' + UNITS_DIR + '/' + k + '.md' })
      log('circuit breaker stood down: ' + onDisk.length + ' units were on disk (writers overran on return only)')
    }
  }

  // 3) VERIFY (disk truth): receipts are CLAIMS, not facts (A41). One cheap probe
  // over every expected unit settles three things at once: writers that finished
  // but overran on return (salvage — no re-buy), writers that returned a receipt
  // without writing the file (RECEIPT-LIED — caught here, not at merge time), and
  // dropped slices. Probe failure falls back to receipts, loudly.
  phase('Verify')
  const onDisk = await diskCheck(expectedKeys, 'Verify')
  if (onDisk === null) {
    log('verify probe unavailable — trusting receipts (degraded)')
    missing = slices.filter(s => !receiptByKey[s.key]).map(s => s.key)
  } else {
    const have = new Set(onDisk)
    const salvaged = expectedKeys.filter(k => have.has(k) && !receiptByKey[k])
    const liars = expectedKeys.filter(k => !have.has(k) && receiptByKey[k])
    if (salvaged.length) log('salvaged from disk (finished, overran on return): ' + salvaged.join(', '))
    if (liars.length) log('RECEIPT-LIED (receipt returned, no unit on disk — A41): ' + liars.join(', '))
    missing = expectedKeys.filter(k => !have.has(k))
  }
  log('verify: ' + (expectedKeys.length - missing.length) + '/' + expectedKeys.length + ' units on disk'
    + (missing.length ? ' — missing: ' + missing.join(', ') : ''))

  // 4) TAIL (targeted): only genuinely missing slices retried, once, escalated (§7).
  phase('Tail')
  if (missing.length) {
    log('tail retry (escalated deadline) for: ' + missing.join(', '))
    const tailSlices = slices.filter(s => missing.includes(s.key))
    const tailResults = await runWatchedWave(tailSlices, s => Math.round(msFor(s) * ESCALATE), 'Tail', 'tail:', writerPrompt)
    const after = await diskCheck(missing, 'Tail')
    missing = after === null
      ? tailSlices.filter((s, j) => !tailResults[j]).map(s => s.key)
      : missing.filter(k => !after.includes(k))
  }

  // 5) TRIAGE + RECOVERY: never the same blind failure three times (§6). A slice
  // that failed the main wave AND the escalated tail gets DIAGNOSED before any
  // third attempt: one batched triage agent (judgement — this is exactly the
  // wrong place for a cheap tier) classifies each failure, and the verdict drives
  // ONE recovery wave — split it, rescope it, retry it, or name it impossible.
  // Bounded by construction: three attempts max per slice, then a diagnosed gap.
  // Bulletproof does not mean "always completes" — a slice can be genuinely
  // impossible (missing input, filtered content). It means no failure is ever
  // retried blind and NO GAP SHIPS UNEXPLAINED.
  phase('Recover')
  if (missing.length) {
    const failed = slices.filter(s => missing.includes(s.key))
    const rawTriage = await spawn(
      'You are TRIAGE for a fan-out. Each slice below failed twice: a normal attempt and an escalated retry. '
      + 'Do NOT redo the work. Inspect the partial evidence (' + UNITS_DIR + '/<key>.progress if present, the run '
      + 'journal) and for each slice decide the single next action with the best chance: '
      + '"split" (too big for one agent — provide 2-4 subSlices), '
      + '"rescope" (the brief is wrong or trips a content filter — provide a narrower brief), '
      + '"retry" (transient failure), or "impossible" (missing input / externally blocked — say exactly why). '
      + 'FAILED SLICES: ' + JSON.stringify(failed.map(s => ({ key: s.key, brief: s.brief, estMinutes: s.estMinutes }))) + ' '
      + 'Return STRICT JSON: an array of {"key","verdict","why","brief"?,"subSlices"?} — nothing else.',
      { label: 'triage', phase: 'Recover' })
    let verdicts = []
    if (rawTriage === null) log('triage unavailable (dropped or died) — defaulting every failed slice to one plain retry')
    else {
      const v = parseJsonLoose(rawTriage)
      if (Array.isArray(v)) verdicts = v
      else log('triage returned non-JSON — defaulting to plain retry')
    }
    const byKey = {}
    for (const v of verdicts) if (v && v.key) byKey[v.key] = v

    const recovery = []
    missing = []
    for (const s of failed) {
      const v = byKey[s.key] || { verdict: 'retry', why: 'no triage verdict returned — plain retry' }
      log('triage "' + s.key + '": ' + v.verdict + ' — ' + (v.why || 'no reason given'))
      if (v.verdict === 'impossible') {
        gapReasons[s.key] = 'triage: ' + (v.why || 'impossible, no reason given')
        missing.push(s.key)
      } else if (v.verdict === 'split' && Array.isArray(v.subSlices) && v.subSlices.length) {
        const subs = v.subSlices.map(x => ({
          key: x.key, brief: x.brief,
          estMinutes: (typeof x.estMinutes === 'number' && x.estMinutes > 0) ? x.estMinutes : s.estMinutes,
          tier: (x.tier === 'mechanical' || x.tier === 'docs-small') ? x.tier : 'judgement',
        }))
        expectedKeys = expectedKeys.filter(k => k !== s.key).concat(subs.map(x => x.key))
        recovery.push(...subs)
      } else if (v.verdict === 'rescope' && v.brief) {
        recovery.push(Object.assign({}, s, { brief: v.brief }))
      } else {
        recovery.push(s)
      }
    }
    if (recovery.length) {
      const recResults = await runWatchedWave(recovery, s => Math.round(msFor(s) * ESCALATE), 'Recover', 'recover:', writerPrompt)
      const still = await diskCheck(recovery.map(s => s.key), 'Recover')
      const failedRec = still === null
        ? recovery.filter((s, j) => !recResults[j]).map(s => s.key)
        : recovery.map(s => s.key).filter(k => !still.includes(k))
      for (const k of failedRec) gapReasons[k] = gapReasons[k] || 'failed after triage-guided recovery (3 attempts total) — diagnose via the journal before any re-run'
      missing = missing.concat(failedRec)
    }
  }

  // 6) REASSEMBLE (critical): a cheap stitch, reading the units FROM DISK — never
  // from the returns (§8). Mechanical only — no fresh analysis — so it stays small,
  // runs on low effort, and finishes in one turn.
  phase('Reassemble')
  manifest = await critical('reassemble', STITCH_MS, () => spawn(
    'You are a mechanical REASSEMBLER — no new analysis. Read every unit file under ' + UNITS_DIR + ' and stitch '
    + 'them, ordered by slice key, into one manifest at ' + OUTDIR + '/manifest.md. For each of these expected slices '
    + 'with NO unit file, write an explicit "MISSING: <key>" line — do not invent content. Expected slices: '
    + expectedKeys.join(', ') + '. Return only the manifest path and a one-line tally (present/missing).',
    { label: 'reassemble', phase: 'Reassemble', effort: 'low', reserveCritical: true }))
} catch (e) { fatal = e }

// 7) GIT POSTFLIGHT: runs even after an abort — an aborted run is MORE likely to
// have left a mess, not less. Compare against the baseline; report, never fix.
phase('Postflight')
const gitFin = gitParse(await spawnGit(GIT_PROBE_PROMPT, { label: 'git:postflight', phase: 'Postflight', agentType: 'Explore', effort: 'low' }), 'postflight')
let gitDrift = null // null = unverified, false = clean, true = drift
if (gitBase && gitFin) {
  const drift = []
  if (gitFin.branch !== gitBase.branch) drift.push('branch ' + gitBase.branch + ' -> ' + gitFin.branch)
  if (gitFin.stashes !== gitBase.stashes) drift.push('stashes ' + gitBase.stashes + ' -> ' + gitFin.stashes)
  if (gitFin.worktrees !== gitBase.worktrees) drift.push('worktrees ' + gitBase.worktrees + ' -> ' + gitFin.worktrees)
  if (gitFin.dirty !== gitBase.dirty) log('GIT: dirty file count ' + gitBase.dirty + ' -> ' + gitFin.dirty + ' (informational — the units dir may live inside the repo)')
  gitDrift = drift.length > 0
  if (gitDrift) log('GIT-DRIFT — an agent broke the git rules: ' + drift.join('; ') + '. NOT auto-fixing; report to the human, they dispose.')
  else log('GIT-OK: branch/stash/worktree state unchanged')
}
if (fatal) throw fatal

// The return value is a RECEIPT of the run, not the work: the units and manifest
// live on disk, and the caller sweeps them — plus the run journal and agent
// transcripts — into the archive before the ephemeral container goes away (§9).
log('run summary: preset=' + SIZE + ' spawned=' + spawned + '/' + AGENT_BUDGET
  + ' watchdogPolls=' + watchSpawned + '/' + WATCH_BUDGET
  + ' git=' + (gitDrift === true ? 'DRIFT' : gitDrift === false ? 'ok' : 'UNVERIFIED')
  + tokenNote()
  + (dropped.length ? ' DROPPED=' + dropped.join(',') : '')
  + (missing.length ? ' RESIDUAL-GAPS=' + missing.join(',') : '')
  + (PENDING_HUMAN_STEPS.length ? ' PENDING-HUMAN-STEPS=' + PENDING_HUMAN_STEPS.length : ''))
return {
  preset: SIZE, slices: slices.length, spawned, watchdogPolls: watchSpawned, dropped,
  residualGaps: missing, gapReasons, manifest, pendingHumanSteps: PENDING_HUMAN_STEPS,
  git: { baseline: gitBase, final: gitFin, drift: gitDrift },
}
