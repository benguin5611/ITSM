# SPEC — <feature>

<!-- The light, single-file spec for small-to-medium work. Graduate to templates/doc-set/ when more than a few files, more than one author, or invariants need their own log. Tag every claim [MV] [DV] [BV] [J] (references/doc-architecture.md). -->

## Purpose and scope
<!-- what this makes true and what it makes unnecessary; in scope; out of scope with an owner for each exclusion -->
<purpose and scope>

## Invariants and decisions
<!-- **INV-<N>** must-not-drift rule · **ADR-<NNNN>** decision · driver · consequence · status. Changing an invariant is re-architecture. -->
<invariants and decisions>

## Requirements
<!-- EARS, one shall per line, stable IDs never renumbered: **REQ-<NNN> (Ubiquitous).** The system shall … -->
<requirements>

## Acceptance
<!-- one check per requirement; a failure is loud and reported, never counted as clean -->
| Requirement | Check |
| --- | --- |
| <REQ> | <how you know it is met> |

## Testing guide
<!-- how to set up, run, and extend the tests; name every field pair that is validated together -->
<testing guide>

## Build sequence
<!-- small gated units in order; each leaves the thing runnable: Do · Verify · Discharges REQ-… -->
1. <unit>

## Verification ledger
<!-- dated: what was verified, how, result -->
| Date | Verified | How | Result |
| --- | --- | --- | --- |
| <date> | <what> | <command> | <result> |
