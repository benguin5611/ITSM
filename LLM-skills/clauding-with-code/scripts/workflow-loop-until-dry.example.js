// workflow-loop-until-dry.example.js — ILLUSTRATIVE reference, not run in production.
//
// PACKAGING NOTICE: this canonical file ships in every Claude.ai skill archive,
// injected at build time by `nix build .#skill-zips`. Edit only this root copy;
// it is intentionally not duplicated in source skill directories.
//
// A different SHAPE of workflow from resilient-workflow.example.js's writer fan-out: a
// READ-ONLY research/audit sweep that repeats itself until it stops finding anything new,
// instead of a fixed-size batch. For the full defense-in-depth ladder (git-bracketed
// writers, watchdog, budgets, triage-guided recovery) see resilient-workflow.example.js —
// this pattern doesn't need most of that because it never touches disk.
//
// Shape: a planner partitions the target into independent CLUSTERS (grouped so one agent
// can read a cluster closely in one pass). Each round, every still-active cluster is
// hunted in parallel; a cluster that finds nothing NEW two rounds running is retired from
// further hunting (its territory is exhausted) while other clusters keep going — cheaper
// than re-scanning a dry cluster every round, and cheaper than one flat "scan everything
// again" loop. Fresh findings are batched per-cluster into ONE adversarial-verification
// call (not one call per finding — the verifier reads the cluster's files once, not N
// times) before being counted as real. A capped MAX_ROUNDS is the backstop against a
// pathological target that never goes quiet.
//
// Distinguish "timed out" from "found nothing": a cluster whose call raced its deadline
// gets retried next round, never penalised toward its dry-streak — the alternative
// (counting a timeout as "nothing found") starves it out of the hunt for a wrong reason.
//
// This file demonstrates the LOOP's control flow only — skills/clauding-with-code/references/
// bug-hunt.md prescribes this exact shape and additionally calls for a watchdog on top of
// per-cluster deadlines (a live run hit flat, too-tight deadlines silently zeroing an
// entire round's findings with no error surfaced); reuse resilient-workflow.example.js's
// `msFor`/watchdog helpers for a run large enough to need one.

export const meta = {
  name: 'loop-until-dry-example',
  description: 'illustrative research/audit sweep: per-cluster hunt, adversarial verification, retire clusters after 2 dry rounds',
  phases: [{ title: 'Plan' }, { title: 'Hunt' }, { title: 'Verify' }, { title: 'Report' }],
}

const A = (typeof args === 'string' ? JSON.parse(args) : args) || {}
if (!A.repo) throw new Error('FAIL-FAST: args.repo is required — refusing to guess a path')
const REPO = A.repo
const MAX_ROUNDS = A.maxRounds || 6
const DRY_LIMIT = A.dryLimit || 2 // consecutive empty rounds before a cluster retires
const HUNT_MS = A.huntMs || 20 * 60 * 1000
const VERIFY_MS = A.verifyMs || 10 * 60 * 1000
const PLAN_MS = A.planMs || 8 * 60 * 1000

const HAS_TIMERS = typeof setTimeout === 'function'
function withDeadline(p, ms, label) {
  if (!HAS_TIMERS) return Promise.resolve(p)
  let t
  const timeout = new Promise((_, rej) => { t = setTimeout(() => rej(new Error('DEADLINE: "' + label + '" exceeded ' + ms + 'ms')), ms) })
  return Promise.race([Promise.resolve(p).then(v => { clearTimeout(t); return v }, e => { clearTimeout(t); throw e }), timeout])
}

const CLUSTER_SCHEMA = { type: 'object', properties: { clusters: { type: 'array', items: {
  type: 'object', properties: { key: { type: 'string' }, brief: { type: 'string' } }, required: ['key', 'brief'] } } }, required: ['clusters'] }
const FINDING_SCHEMA = { type: 'object', properties: { findings: { type: 'array', items: {
  type: 'object', properties: {
    title: { type: 'string' }, file: { type: 'string' }, line: { type: 'integer' },
    summary: { type: 'string' }, failure_scenario: { type: 'string', description: 'concrete input/state that makes this a real problem' },
  }, required: ['title', 'summary', 'failure_scenario'] } } }, required: ['findings'] }
const VERDICT_SCHEMA = { type: 'object', properties: { verdicts: { type: 'array', items: {
  type: 'object', properties: { title: { type: 'string' }, verdict: { type: 'string', enum: ['CONFIRMED', 'INVALID', 'PARTIAL'] }, reasoning: { type: 'string' } },
  required: ['title', 'verdict', 'reasoning'] } } }, required: ['verdicts'] }

function findingKey(f) { return (f.file || '?') + ':' + (f.line || 0) + ':' + String(f.title || '').toLowerCase().slice(0, 60) }

phase('Plan')
const plan = await withDeadline(
  agent('Partition ' + REPO + ' into independent clusters a single agent can read closely in one pass '
    + '(batch related files together — do not over-split). Return each cluster\'s key and a brief naming its actual files/dirs.',
    { label: 'plan', phase: 'Plan', agentType: 'Explore', schema: CLUSTER_SCHEMA }),
  PLAN_MS, 'plan')
const clusters = (plan && Array.isArray(plan.clusters)) ? plan.clusters : []
if (!clusters.length) throw new Error('FAIL-FAST: planner returned no clusters — nothing to hunt')
log('planner produced ' + clusters.length + ' clusters')

phase('Hunt')
let active = clusters.slice()
const dryStreak = {}
clusters.forEach(c => { dryStreak[c.key] = 0 })
const seen = new Set()
const confirmed = []
let round = 0

while (round < MAX_ROUNDS && active.length) {
  round++
  const priorTitles = [...seen].map(k => k.split(':').slice(2).join(':'))
  const huntResults = await parallel(active.map(c => () =>
    withDeadline(agent(
      'Hunt cluster: ' + c.brief + ' (round ' + round + '/' + MAX_ROUNDS + '). '
        + (priorTitles.length ? 'Already reported, do NOT repeat: ' + priorTitles.slice(0, 40).join(' | ') + '. ' : '')
        + 'Give each finding a concrete failure_scenario, not a vague concern. Only report what you are confident is real.',
      { label: 'hunt:' + c.key, phase: 'Hunt', agentType: 'Explore', schema: FINDING_SCHEMA }),
      HUNT_MS, 'hunt:' + c.key).catch(e => { log('DROP hunt:' + c.key + ': ' + (e && e.message)); return null })
  ))

  const timedOut = {}
  const roundFindings = []
  huntResults.forEach((r, i) => {
    const c = active[i]
    if (r === null) { timedOut[c.key] = true; return }
    ;(r.findings || []).forEach(f => roundFindings.push(Object.assign({ cluster: c.key }, f)))
  })
  const fresh = roundFindings.filter(f => !seen.has(findingKey(f)))
  fresh.forEach(f => seen.add(findingKey(f)))
  log('round ' + round + ': ' + roundFindings.length + ' raw, ' + fresh.length + ' fresh, ' + Object.keys(timedOut).length + ' timed out')

  if (fresh.length) {
    phase('Verify')
    const byCluster = {}
    fresh.forEach(f => { (byCluster[f.cluster] = byCluster[f.cluster] || []).push(f) })
    const keys = Object.keys(byCluster)
    const verdicts = await parallel(keys.map(k => () =>
      withDeadline(agent(
        'Adversarially verify these ' + byCluster[k].length + ' candidate findings. Read the actual current source '
          + 'yourself before judging each — do not trust the description. Give each a verdict.\n\n'
          + byCluster[k].map((f, i) => (i + 1) + '. "' + f.title + '" — ' + f.summary + ' (' + f.failure_scenario + ')').join('\n'),
        { label: 'verify:' + k, phase: 'Verify', agentType: 'Explore', schema: VERDICT_SCHEMA }),
        VERIFY_MS, 'verify:' + k).catch(e => { log('DROP verify:' + k + ': ' + (e && e.message)); return null })
    ))
    verdicts.forEach((v, i) => {
      const k = keys[i]
      if (!v || !Array.isArray(v.verdicts)) return
      const byTitle = {}
      v.verdicts.forEach(x => { byTitle[x.title] = x })
      byCluster[k].forEach(f => {
        const vd = byTitle[f.title]
        if (vd && (vd.verdict === 'CONFIRMED' || vd.verdict === 'PARTIAL')) confirmed.push(Object.assign({}, f, { verdict: vd.verdict }))
      })
    })
    phase('Hunt')
  }

  const freshByCluster = {}
  fresh.forEach(f => { freshByCluster[f.cluster] = (freshByCluster[f.cluster] || 0) + 1 })
  active = active.filter(c => {
    if (freshByCluster[c.key]) { dryStreak[c.key] = 0; return true }
    if (timedOut[c.key]) return true // a timeout is never evidence the cluster is exhausted
    dryStreak[c.key]++
    if (dryStreak[c.key] >= DRY_LIMIT) { log('cluster "' + c.key + '" dry ' + DRY_LIMIT + ' rounds — retired'); return false }
    return true
  })
}
if (round >= MAX_ROUNDS && active.length) log('MAX_ROUNDS hit with ' + active.length + ' cluster(s) still active — capped, not exhausted')

phase('Report')
log('summary: rounds=' + round + '/' + MAX_ROUNDS + ' clusters=' + clusters.length + ' confirmed=' + confirmed.length)
return { rounds: round, clusters: clusters.length, confirmed }
