# SPEC — <project>

<!-- The authoritative requirements document. Invariants live here and cite ADR files; build steps that discharge each requirement live in build_plan.json. Tag every claim [MV] [DV] [BV] [J]. -->

## Purpose and exit criteria
<!-- what this exists to make true; the measurable criteria that say it is complete, not "ran without error" -->
<purpose and exit criteria>

## Invariants
<!-- decisions that must not drift; changing one is a new ADR plus re-review -->
| ID | Invariant | Decided by |
| --- | --- | --- |
| <INV-N> | <must-not-drift rule> | <ADR-NNNN> |

## Components
<!-- the shape of the thing: parts, interfaces, what generates what -->
<components>

## Requirements
<!-- grouped by domain under `### <DOMAIN>`; one shall per line: **REQ-<DOMAIN>-<NNN> (Ubiquitous).** The system shall … -->
<requirements>

## Data contracts
<!-- every shape that crosses a boundary, with a schema or worked example; [MV] once validated against the real thing -->
<data contracts>

## Non-functional
<!-- only what applies: reproducibility, idempotency, logging without secrets or PII, observability, failure posture -->
<non-functional requirements>

## Safety gate
<!-- any hard guard the system must never bypass, stated as an invariant-backed requirement -->
<safety gate, or none — reason>

## Acceptance
<!-- the concrete check per requirement; a failure is a typed outcome, never counted as clean -->
| Requirement | Check |
| --- | --- |
| <REQ> | <check> |

## Testing guide
<!-- set up, run, extend; name every field pair validated together in one fixture -->
<testing guide>

## Out of scope
| Excluded | Owned by |
| --- | --- |
| <thing> | <owner> |

## Verification ledger
| Date | Verified | How | Result |
| --- | --- | --- | --- |
| <date> | <what> | <command> | <result> |
