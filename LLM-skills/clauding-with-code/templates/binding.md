# Binding — <project>

<!-- The project facts the skill binds to (docs/binding.md in the target repo). Every section is required; a `<placeholder>` counts as empty. -->

## Stack
<!-- one line per layer: language + version, framework, storage, auth -->
<stack>

## Gate commands
<!-- runs on every unit before commit; this is the gate — CI, if any, only re-runs it -->
| Step | Command | Pin |
| --- | --- | --- |
| lint | <command> | <version> |
| format | <command> | <version> |
| types | <command> | <version> |
| tests | <command> | <version> |
| docs | driftguard check --staged | <version> |

<target OS and runtime the gate must pass on>

## Breaking-change oracle
<!-- diffs the public contract against the release baseline -->
<command, or none — reason>

## CI
<!-- mirrors the gate commands; never the gate -->
<none, or path/to/workflow>

## Tracker
| Field | Value |
| --- | --- |
| system | <tracker system, or none> |
| key prefix | <PROJ-> |
| branch | <PROJ-NNN/short-slug> |
| commit subject | <type(scope): PROJ-NNN summary> |
| PR title | <type(scope): PROJ-NNN summary> |

## Merge policy
| Rule | Value |
| --- | --- |
| method | <squash, merge, rebase> |
| direct push to trunk | <never, or the ledger file only> |
| stacked PRs | <yes or no> |
| standing bypass | <none, or its blast-radius scope> |

## Model tiers
| Tier | Model | Use for |
| --- | --- | --- |
| cheap | <model> | mechanical bulk |
| default | <model> | most units |
| strong | <model> | judgement, security, concurrency |

## Replica
<!-- production-like environment; env-var rules that break tests -->
| Step | Command |
| --- | --- |
| up | <command> |
| down | <command> |
| env | <VAR rules> |

## Review skills
| Lens | Skill |
| --- | --- |
| review | <meta-code-review> |
| security | <security skill, or owasp-top-10> |

## Paths
| Purpose | Path |
| --- | --- |
| docs | <docs/> |
| spec | <docs/SPEC.md, or the doc set> |
| archive | <docs/archive/> |

## Policies
<!-- org rules an agent must obey here -->
- <rule>
