# Engineering

Principles decide when the rules do not cover the case. Principles over process.

## What you build

Think big, start small: ship the smallest slice and improve. The interface is the product: every
endpoint, flag and error message is a customer-facing decision, and "it's just internal" is never true.
Prior art first: adopt, then steal the proven design, then build only the part that does not exist.
Be opinionated and hold it loosely: recommend with reasons, update on evidence. When a finding is N
things wrong the same way, lead with the design that makes the next one impossible and offer the N
fixes as the interim step.

## How you sequence

Finish before you start: partially-done work is the most expensive thing in software. Small,
frequent, reversible: a two-thousand-line PR is a hostage situation; prefer the decision you can
undo. Slices a day to three days long, each shippable and testable alone. Make it work, make it right,
make it fast — in that order, and do not skip the middle. Build what the card says; raise a new card
for the next improvement; when you de-scope, say so.

## Before you build

An AI-drafted document is a first draft, not a design and not a green light: think against it,
validate it against the real data model, interfaces and permission model, then commit. Name every
trade-off out loud and write it down where the next reader will find it. Distinguish "done this before,
two days" from "new territory, spike it first". Assume you will be wrong: tests, monitoring, flags and
evolvable interfaces are how a system survives it.

## Owning what ships

Operability is a feature: structured logs without secrets or personal data, error handling,
graceful degradation, a story for the 2am debugger. Test behaviour, not implementation. Security is
part of every unit: validate inputs, check permissions at every entry point, think about the caller
with a different tenant's ID. Leave the code better than you found it in small ways, without turning a
feature into a refactor.

## Working with others

Communicate through artefacts — a design doc, a PR body, a decision record — not meetings that leave
nothing written. Share thinking early and signal progress. Ask for help after framing the question
well and before burning a day. No single point of failure in systems or people. Review is first-class
work: specific, constructive, about correctness and safety, never a rubber stamp or a formatting
drive-by. Know who the work is for. Treat AI output as a junior colleague's first draft: read every
line before it is yours.

## Clean code

Name for the reader, in the language's conventions, consistently. Format with a tool. A comment
earns its place only by stating what the code cannot: a hidden constraint, an invariant, a workaround
for a specific bug. Never a narrated debugging journey, never a defence of a choice nobody challenged,
never a review ID or a date; if deleting it would confuse nobody, delete it. Functions with one job,
short, shallow. Design for the test: single responsibilities, injected dependencies, pure functions
where the logic allows, no environment values in code. Unit tests cover the normal, edge and error
paths and assert something meaningful; refactor tests with the code. Static analysis runs
automatically, same config everywhere, findings fixed promptly. Documentation is for the next reader
and is current or it is worse than none.

## Hygiene the gate enforces

Lint every artefact type at zero warnings — code, shell, markdown, YAML, JSON, workflows — through the
same runner locally and, where CI exists, there. Every suppression is rule-coded and justified inline.
A shared helper that exists gets used: `DG-ADOPTION` fails a bypass unless the enclosing function says
why. Test fixtures satisfy the shape a test checks without looking like real secrets. No hardcoded
paths: flag → environment → config → computed default, XDG directories, 12-factor config. No hardcoded
derived facts: name the registry, do not type its count. No personal data or secrets in logs by
default — tag fields at the model boundary and verify redaction on a real sample.

## Agent-first command lines

If the deliverable has a CLI, make it legible to an agent without requiring one: stdout carries only
parseable data, stderr carries progress; a noun-verb hierarchy; distinct documented exit codes and
never zero on failure; structured errors with a hint; unknown flags are hard failures; the surface is a
versioned contract; commands idempotent, input via stdin or file; inputs validated against the
mistakes agents make (traversal, double encoding, control characters). Any tool manifest is generated
from the CLI's own self-description, never hand-kept.
