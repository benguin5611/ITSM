// resilient-workflow.example.js — ILLUSTRATIVE reference, not run in production.
//
// A minimal, project-agnostic workflow showing the orchestration-economy patterns
// (see ../references/orchestration-economy.md) on a runtime that exposes:
//   agent(prompt, opts) -> Promise<string>   one sub-agent call
//   parallel(thunks)    -> Promise<any[]>     run thunks concurrently, await all
//   phase(title)        -> void               mark a pipeline phase (for the UI/log)
//   log(msg)            -> void               structured log line
//
// The shape mirrors a typical multi-agent review workflow script. The pipeline
// here is deliberately tiny — a PLANNER decides a partition, a waved WRITER fan-out
// fills each slice, and a cheap REASSEMBLE stitches the manifest — so the guards are
// the point, not the work.

export const meta = {
  name: 'resilient-workflow-example',
  description: 'illustrative resilient fan-out: guarded planner -> waved writer fan-out -> reassemble (demonstrates withDeadline / critical / inWaves)',
  phases: [
    { title: 'Plan' },
    { title: 'Write' },
    { title: 'Reassemble' },
  ],
}

// ---- Backstop deadlines: GENEROUS, not the stall detector. ------------------
// These are coarse backstops whose only job is to turn a TRUE hang into a loud
// abort. They are intentionally long: a tight timer cannot tell slow-but-alive
// from hung, and on a fan-out it would wrongly count queue time against a worker
// that has not started yet. The real liveness signal is PROGRESS (are artefacts
// /transcripts still growing?), watched by a harness-managed wake-up — NOT a
// background shell loop (those get reaped mid-watch). See orchestration-economy §4.
const PLAN_MS  = (args && args.planMs)  || 8  * 60 * 1000 // planner: small, but a single point of failure
const WRITE_MS = (args && args.writeMs) || 10 * 60 * 1000 // one writer slice: bounded so a barrier never wedges
const STITCH_MS = (args && args.stitchMs) || 6 * 60 * 1000 // reassembly: cheap, still bounded

// ---- withDeadline: bound any promise. ---------------------------------------
// If the sandbox has no timers, degrade — but say so LOUDLY: silently running
// unbounded would defeat the NO SILENT HANG discipline while appearing to enforce
// it. No Date.now anywhere — we race against a timer, we do not poll a clock (a
// clock read tells you elapsed time, which is exactly the wrong signal; see §4).
// Inside parallel(), callers turn a rejection into null so one slow worker
// degrades to a gap instead of wedging the whole barrier.
const HAS_TIMERS = typeof setTimeout === 'function'
if (!HAS_TIMERS) log('WARNING: no timers in this sandbox — deadline bounding is OFF; rely on the watchdog wake-up')
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

// ---- critical: guard a sequential single-point-of-failure step. -------------
// Bound it, retry ONCE (transient flakes happen), then abort LOUDLY with a resume
// hint — never hang silently. The hint matters because a resume re-evaluates the
// whole script top-to-bottom: re-pass args (keep them in a file) and DIAGNOSE
// before resuming — never resume blindly into the same failure twice (§6). And
// remember a loud abort is NOT proof the work wasn't done: an agent can finish its
// output and only overrun on its RETURN — inspect the artefact on disk first (§5).
async function critical(label, ms, makeCall) {
  for (let attempt = 1; attempt <= 2; attempt++) {
    try { return await withDeadline(makeCall(), ms, label) }
    catch (e) {
      log('CRITICAL "' + label + '" attempt ' + attempt + '/2 failed: ' + (e && e.message))
      if (attempt === 2) {
        throw new Error('FAIL-FAST: critical step "' + label + '" stalled/failed twice (' + ms + 'ms each). '
          + 'Before resuming: (1) check whether its output already exists on disk — it may have finished and only '
          + 'overrun on return; (2) diagnose (bound or split the step), do not resume blindly into the same hang; '
          + '(3) re-pass args (from the args file). Then resume from cache so only this step re-runs.')
      }
    }
  }
}

// Guarded fan-out thunk: a slow worker degrades to null instead of wedging the
// barrier. The reassembly step treats a null slice as a gap to finish cheaply (§7),
// NOT as a reason to re-run everything.
const bounded = (label, ms, thunk) => () =>
  withDeadline(thunk(), ms, label).catch(e => { log('fan-out "' + label + '" dropped: ' + (e && e.message)); return null })

// ---- inWaves: run a large fan-out in waves of ~10. --------------------------
// The runtime caps true concurrency, so submitting 100+ thunks at once just queues
// the tail — and the queued agents burn their own deadline WAITING for a slot, a
// real mass-timeout cause (§2). Feeding work in waves means every agent in a wave
// starts executing immediately; its deadline only ever covers its own run, never
// queue time.
async function inWaves(items, waveSize, thunkOf) {
  const out = []
  for (let i = 0; i < items.length; i += waveSize) {
    const wave = items.slice(i, i + waveSize)
    log('wave ' + (i / waveSize + 1) + ': ' + wave.length + ' agents (items ' + i + '..' + (i + wave.length - 1) + ')')
    const results = await parallel(wave.map(thunkOf)) // launch the wave, await it, THEN the next
    for (const r of results) out.push(r)
  }
  return out
}

// ---- config (keep inputs in args/a file so a resume re-passes them; §6). -----
const A = args || {}
const REPO = A.repo || '.'
const OUTDIR = A.outDir || '.'
const WAVE_SIZE = A.waveSize || 10 // ~ the runtime's real concurrency cap

// ---- pipeline ---------------------------------------------------------------

// 1) PLANNER (critical): reads only COMPACT summaries and decides the partition
// of work. It does NOT read everything and it does NOT write everything — that
// read-all/write-all monolith would blow any deadline (§3). It is small, fast,
// and a single point of failure, so it is guarded by critical().
phase('Plan')
const planJson = await critical('plan', PLAN_MS, () => agent(
  'You are the PLANNER. Read only the high-level summaries under ' + REPO + ' (do NOT open every file). '
  + 'Decide how to PARTITION the work into independent slices a writer can each own in isolation. '
  + 'Return STRICT JSON: an array of {"key","brief"} — nothing else.',
  { label: 'plan', phase: 'Plan', agentType: 'Explore' }))

let slices = []
try { slices = JSON.parse(planJson) } catch (e) { log('planner did not return JSON: ' + (e && e.message)) }
log('planner produced ' + slices.length + ' slices')
// Zero slices means the whole run would "succeed" doing nothing — fail LOUDLY instead
// of silently completing empty. (Or use the agent() schema option, which validates and
// retries the structured output at the tool layer and removes this failure mode.)
if (!slices.length) throw new Error('FAIL-FAST: planner returned no usable slices — nothing to write; fix the planner prompt/output before resuming')

// 2) WRITERS (waved fan-out): one worker per slice, each reads ONLY its slice and
// writes ONE unit. Bounded so a single slow writer degrades to null; waved so no
// writer waits in a queue burning its deadline.
phase('Write')
const written = await inWaves(slices, WAVE_SIZE, (s) =>
  bounded('write:' + s.key, WRITE_MS, () => agent(
    'You are ONE writer. Read ONLY your slice (' + s.brief + ') under ' + REPO + '. '
    + 'Produce exactly one self-contained unit for this slice. Do not touch other slices.',
    { label: 'write:' + s.key, phase: 'Write' })))

const done = written.filter(Boolean)
const missing = slices.filter((_, i) => !written[i]).map(s => s.key)
log('writers: ' + done.length + '/' + slices.length + ' slices returned'
  + (missing.length ? ' — finish-the-tail-cheap for: ' + missing.join(', ') : ''))
// Per §7: if a small tail is missing, complete just those keys with one or two
// targeted writers (or by hand) — do NOT re-run the whole fan-out.

// 3) REASSEMBLE (critical): a cheap stitch into the manifest downstream expects.
// Mechanical only — no fresh analysis — so it stays small and finishes in one turn.
phase('Reassemble')
const manifest = await critical('reassemble', STITCH_MS, () => agent(
  'You are a mechanical REASSEMBLER — no new analysis. Stitch the writer units below into one ordered '
  + 'manifest and write it to ' + OUTDIR + '/manifest.md. Note any gaps verbatim; do not invent missing units. '
  + 'Return only the path and a one-line tally.\n\nUNITS:\n' + done.join('\n\n---\n\n'),
  { label: 'reassemble', phase: 'Reassemble' }))

return { slices: slices.length, written: done.length, missing, manifest }
