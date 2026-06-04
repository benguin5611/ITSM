# Code grounding — regenerate + verify (last responsible moment)

Ground truth is the running code, not the artefact. Regenerate the code map right before fan-out and personally spot-check it; the spec always lags.

## Method
1. **Scope the delta.** `git -C <repo> log --oneline <last-grounding>..HEAD` and `git -C <repo> status --short`. Record the exact `HEAD`. If the working tree is dirty, the review reads the on-disk state — note it.
2. **Regenerate the map** against current code (one inventory agent, or reuse the conventions of your stack-specific security-audit skill): real excerpts with `file:line`, never paraphrase unread behaviour, sections per subsystem, an explicit "as-built surprises" list, NO security judgments (inventory only).
3. **Spot-check the load-bearing claims yourself** — the kill-switch / fail-open-vs-closed, masking splits, any live-session re-scoping, the migration set. This is where stale-spec contradictions surface *before* the expensive fan-out.
4. **Record naming reality.** If the brief names an RPC/handler/symbol that does not exist, correct it everywhere — a phantom name silently misdirects every downstream agent.
5. **Freshness.** If the branch is moving, either freeze it or re-confirm `HEAD` immediately before launch and abort if it moved (see anti-pattern A3).

## CODE-WINS discipline
Where code and artefact disagree, the **code** is correct and the artefact is stale — every mismatch is a finding to correct the artefact, never a reason to change code to match the doc. Re-verify previously-corrected claims still hold (recent commits may have moved them again). "EXISTS" coverage claims lie unless the named test actually proves the requirement on a complete, non-fail-fast run.
