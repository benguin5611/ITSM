<!--
  session-handover.md — a resume/handover doc so a FRESH session can pick up mid-build of
  <feature name> with zero loss of context (clauding-with-code: keep the run resumable).

  Write this for a reader who has NONE of your context. They should be able to read it top to
  bottom and continue the build correctly: know the current state, the standing rules, where
  everything is, the exact commands to resume, how the checkpoint flow works, and what they must
  NOT do. Update it at every checkpoint so it never goes stale. Australian English. Descriptive
  headings, no numbers.
-->

# <feature name> — session handover

**As at:** `<date/time>` · **Baseline SHA:** `<HEAD SHA>` · **Branch:** `<branch name>` ·
**Worktree:** `<absolute path>`

<!-- One paragraph: where the build is overall and the single most important thing the next session
     should know before touching anything. -->

`<state-of-play summary>`

## Current state

<!-- The honest snapshot, split three ways. Be specific — name files, units, commands in flight. -->

**Done (committed, green):**
- `<unit / artefact>` — `<commit SHA / file:line>`

**In flight (started, not finished):**
- `<unit>` — `<where it stands, what is left, any uncommitted work>`

**Blocked / waiting:**
- `<unit>` — *blocked on* `<dependency / human decision / env issue>`

## Standing rules

<!-- The non-negotiables this run operates under, so a fresh session does not relearn them the hard
     way. Carry forward the prime directives plus any project-specific rules bound for this run. -->

- Secure & private by design; fail closed; threat-model before building.
- Match existing codebase conventions; the reader should not tell which file was AI-written.
- Minimise additions (no new tool/file/dep/abstraction unless genuinely necessary); simplest thing
  that is correct and secure wins.
- Build loop every unit: *small unit → lint → local CI-mirror (fail-fast) → commit → push only when
  green.* Never bypass lint or commit hooks.
- Never push to a remote until the human explicitly says so.
- `<project-specific rule>` / `<project-specific rule>`

## Key paths

<!-- Everything the next session needs to find, by absolute path. -->

- *Spec:* `<path to SPEC.md>`
- *Plan & variances:* `<path to plan-and-variances.md>`
- *Discovery-gate artefacts:* `<path>`
- *Working / archive folder:* `<path>`
- *This handover:* `<path>`

## Resume / launch commands

<!-- The EXACT commands to get from a cold start to actively building again, in order. Include any
     args/env that must be re-passed (a resume that drops its arguments is a silent failure). Make
     them copy-pasteable; use absolute paths and `git -C <path>` rather than `cd`. -->

```
<command to enter the worktree / set up env>
<command to bring up the production-replica stack>
<command to run the test suite / CI mirror>
<command/args to resume the build from where it left off — re-pass all required args>
```

*Resume trigger / args to re-pass:* `<trigger word or args, exactly>`

## Checkpoint flow

<!-- How this run pauses for the human and emits durable progress. So the next session knows when to
     stop and hand back, and what to produce at each pause. -->

- Each phase has an exit artefact and a human checkpoint; do not enter a phase until the prior
  checkpoint is signed off.
- At each checkpoint: surface options + a recommendation at any real fork; update the spec, the
  plan/variances log, and THIS handover; then wait for the human.
- Surface blockers immediately and loudly — never wait silently on a stall.
- *Next checkpoint due:* `<what triggers it / what to present>`

## Do NOT

<!-- The sharp edges. Specific "do not do X" items that would lose work, break the run, or violate a
     rule. Add the ones learned on THIS build as they come up. -->

- Do NOT push to any remote without explicit human sign-off.
- Do NOT bypass linters or commit hooks (no `--no-verify`).
- Do NOT run a second agent/session against this same working tree — isolate in its own worktree.
- Do NOT edit the plan to hide a deviation — record it in the variances log instead.
- Do NOT delete working artefacts outright; move them to the archive (recoverable delete only).
- Do NOT resume without re-passing the required args above.
- `<build-specific landmine>`
