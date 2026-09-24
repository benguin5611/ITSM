# Handover — <feature>

<!-- For a fresh session with none of your context. You are not the author; if agents run in parallel here, pick your own identifier and check it for collisions. Update at every checkpoint. -->

| As at | Baseline SHA | Branch | Worktree |
| --- | --- | --- | --- |
| <date time> | <sha> | <branch> | <absolute path> |

<one paragraph: where the build is and the single most important thing to know before touching anything>

## Current state
| State | Unit | Detail |
| --- | --- | --- |
| done | <unit> | <commit, file:line> |
| in flight | <unit> | <what is left, uncommitted work> |
| blocked | <unit> | <blocked on> |

## Rules
<!-- do not restate: the prime directives are in SKILL.md, the project rules in docs/binding.md; list only this run's additions -->
- <run-specific rule>

## Paths
| Artefact | Path |
| --- | --- |
| spec | <path> |
| build plan | <path> |
| gate artefact | <path> |
| archive | <path> |

## Resume
<!-- exact copy-pasteable commands from cold start, absolute paths, every argument a resume must re-pass -->
```text
<command>
```

## Next checkpoint
<what triggers it and what to present>

## Do not
- <landmine learned on this build>
