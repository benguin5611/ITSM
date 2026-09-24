# AGENTS — <project>

<!-- The file an agent reads first. Commands and the few rules that would burn an agent who skipped them; everything else is a pointer. 25–75 lines is the healthy range. -->

## What this is
<one or two lines; link docs/SPEC.md for the rest>

## Commands
The gate commands, pins and replica bring-up are in `docs/binding.md`. Run the gate before every commit; hooks are never bypassed.

## Key rules
- <the two or three things that would burn an agent who skipped them>

## Docs
Read `docs/CONVENTIONS.md` before editing any document. `docs/generated/` is written by `driftguard write`, never by hand.

## Parallel agents
<!-- delete this section on a solo project -->
Concurrent agents run here. Read `docs/AGENT_CLAIMS.md` before touching git state: self-assign an identifier, work in your own worktree, claim before building, release when your PR opens. The merge rule is in the ledger's header.
