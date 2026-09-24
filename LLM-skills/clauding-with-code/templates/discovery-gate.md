# Discovery gate — <feature>

<!-- Phase 0 exit artefact; no code until filled and signed off. A `<placeholder>` counts as empty; nothing to record reads `none — reason`. -->

## Need
<!-- who needs this, what it makes true, what it makes unnecessary -->
<need>

## Prior art
<!-- search twice per surface: what builds it, what tests it; ≥2 candidates or `single candidate — reason`; verdict is adopt, steal or build -->
| Candidate | Builds or tests | Verdict | Reason |
| --- | --- | --- | --- |
| <candidate> | <builds> | <verdict> | <reason> |

## Coupling map
<!-- every "shared" or "generic" component this builds on; decision is build on, decouple or new -->
| Component | Real couplings | Decision |
| --- | --- | --- |
| <component> | <couplings> | <decision> |

## Assumptions
<!-- Status is `verified` or `unverified`; unverified needs `accepted-risk: name, date` in Check -->
| Assumption | Status | Check |
| --- | --- | --- |
| <assumption> | <status> | <command, or accepted-risk: name, date> |

## Gate commands and environment
<!-- what the replica cannot reproduce, target OS vs dev machine, how each gap is exercised before ship -->
<environment gaps and how each is covered>

## Names
<!-- new terms; every rename and the layers it cascades through -->
| Term or rename | Definition, or layers touched | Collides with |
| --- | --- | --- |
| <term> | <definition> | <none, or the existing thing> |

## Contract and breaking-change budget
<!-- run the oracle from binding.md; one row per break; decision is accept or bridge -->
| Break | Who binds to it | Decision |
| --- | --- | --- |
| <break, or none — oracle clean> | <consumers> | <decision> |

## Filterability and observability
<!-- each new field: filterable? each new handler or job: span attributes -->
| Field or handler | Decision |
| --- | --- |
| <name> | <decision> |

## Threats and privacy
<!-- STRIDE sized to the change; personal-data inventory; every high or critical threat gets a row -->
| Threat or data | Disposition | Ref |
| --- | --- | --- |
| <threat> | <mitigate, accept> | <ADR or test> |

## Open forks
<!-- every call a reasonable person could make differently; the human decides, in their words -->
| Fork | Options | Recommendation | Decision |
| --- | --- | --- | --- |
| <fork> | <options> | <recommendation and why> | <decision, who, date> |

## Declined alternatives
<!-- so a later pass does not resurrect them -->
| Alternative | Declined by | Date | Reason |
| --- | --- | --- | --- |
| <alternative> | <name> | <date> | <reason> |

## Sign-off
<!-- Phase 1 is blocked until this reads `signed-off: name, date` -->
<signed-off: name, date>
