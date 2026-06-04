# Composition map — which lens per scope, and how outputs reconcile

meta-code-review composes existing skills; it does not review directly. Pick by scope, then de-duplicate and arbitrate.

## Lens selection
| Scope / artefact | Lens(es) | Run via |
|---|---|---|
| Plan / design / strategy soundness | `rainbow-team-review` (adversarial, 10 roles + Judge) | interactive (or workflow for the full panel) |
| Whole-codebase / cross-cutting security | a stack-specific security-audit skill (e.g. `owasp-top-10`'s deep mode) | workflow (heavy) |
| Changed-files / PR security | `owasp-top-10` | interactive |
| Complexity / cleanup of changed code | `/simplify` | interactive |
| Dead / orphaned code after deletions | in-house dead-code swarm (finders → collator → grudge arbiter) | workflow (heavy) |
| Adversarial defect hunt on AI-generated code | in-house grudge adjudicator | workflow (heavy) |
| Spec / test-suite evolution across versions | all of the above, composed | interactive + heavy passes on opt-in |

## Domain overlays

When the changeset is detected as domain-specific (or the user specifies `--domain=`), load the matching overlay from `references/domain-*.md` before lens selection. The overlay extends the lens table above and adds domain-specific anti-patterns and ROI gates. A changeset spanning multiple domains loads all relevant overlays; confirm scope at the discovery gate before fan-out.

**Auto-detection signals:**
| Domain | File patterns |
|---|---|
| Frontend | `.vue`, `.ts` in `web/`, `*_pb.ts`, `vitest.config*`, FormKit schema files |
| Backend | `.go`, `.proto`, `sqlc.yaml`, `*.sql` in `db/`, `buf.gen.yaml`, `buf.work.yaml` |
| Infrastructure | `*.tf`, `*.tfvars`, `docker-compose*.yml`, `Dockerfile*`, `.github/workflows/*.yml`, `keycloak*.sql` |

## Reconciliation rules
- **De-duplicate across lenses** before acting — the same issue surfaces under multiple roles; merge to one finding with the strongest evidence.
- **Arbitrate conflicts** with the prime-directive precedence (security/privacy > convention-match > no-new-deps > simplicity) and CODE-WINS for descriptions.
- **Verify every finding** against ground truth before it enters the artefact (directive 4). A "finding" that the code already mitigates is dropped, naming where the mitigation lives.
- **One artefact, one decision record.** Lens outputs feed the synthesis; they are not the deliverable.
- **Scale to the ask.** A quick check uses a couple of lenses; "be comprehensive / thoroughly audit" warrants the heavy passes + an adversarial verify pass — but only after the discovery gate sign-off.
- **Orchestration economy (lean by default).** Agents + tokens are budgeted (engineering-precedence #3/#4 applied to the orchestration). Do NOT fan out one agent per artefact, nor an attacker/defender A+B pair per artefact — **select** the high-signal subset, **batch** small inputs into one agent, **one analyst per item** unless an adversarial split genuinely earns its place. Target a handful of agents by default — an order of magnitude cheaper than a sprawling many-agent run; the full panel + swarm is opt-in only. Note the tension: *mining the whole journey* (reading all versions / the failure trail) is about **what you read**, achieved via selection + batching — not one agent per artefact.
