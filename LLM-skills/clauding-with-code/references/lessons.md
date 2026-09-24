# Lessons — the failure catalogue behind the root causes

Not loaded in a run. Each row is one real failure, generalised, that a root cause in
`root-causes.md` now covers with a check. Numbers are permanent: a new lesson appends A71+, a
retired one keeps its row with RC `retired`. `RC —` means prose only, no check.

| A | RC | Instance | Check |
| --- | --- | --- | --- |
| A1 | RC7 | A "generic" session table was wired into an unrelated verification flow; building on it would have entangled two features | gate Coupling map |
| A2 | RC7 | A one-click emailed link was consumed by corporate mail scanners before any human saw it; any GET with a side effect is | gate Gate commands and environment |
| A3 | RC1 | Two defects invisible to local tests surfaced only against a production replica (a pre-auth flag read, a tenancy guard at boot) | binding Replica; `verify_test` run live |
| A4 | RC7 | Lint and build failures first seen in CI because hooks were bypassed to move faster | binding Gate commands; hooks never bypassed |
| A5 | RC4 | An unbounded long step wedged with no output; only a human looking noticed | resilient-workflow deadline + watchdog |
| A6 | RC4 | One agent read everything then wrote everything; unresumable, unparallelisable | resilient-workflow planner + writers |
| A7 | RC4 | Hand-rolled deadlines counted queue time; a 50-agent submission timed out agents that never started | resilient-workflow waves |
| A8 | RC4 | A whole multi-hour run was restarted to recover two failed slices | resilient-workflow tail retry |
| A9 | RC1 | A branch split into PRs from memory dropped files; git was never asked | landing.md empty-diff invariant |
| A10 | — | A spec fragmented across sibling docs left no single source of truth | templates: one SPEC |
| A11 | RC5 | A test-status ledger shipped as the testing story; nobody could re-run it | SPEC Testing guide required |
| A12 | — | Scratch files and resume scaffolding left after completion read as live | landing.md Phase 5 checklist |
| A13 | RC1 | A spec asserted coverage the code did not provide | verification tags; ledger rows |
| A14 | RC4 | ~178 agents over ~5 hours for one feature; most cost was queue tail and duplicate reads | resilient-workflow budget counter |
| A15 | RC6 | Company and stack names leaked into reusable skill text | binding lives in the target repo; LINT-PUBLIC |
| A16 | RC7 | Three unrelated things shared one name; a rename cascaded through six layers and re-opened twice, once silently inside an unrelated commit | gate Names |
| A17 | RC7 | A proto field number was reused with a new meaning; grep called it safe, the breaking-change linter did not | binding Breaking-change oracle; gate Contract |
| A18 | RC1 | A zero-hit grep was treated as proof a removal was safe; the symbol was load-bearing | oracle per artefact class (`landing.md`) |
| A19 | RC7 | Issued links were not enumerable or revocable | gate Threats and privacy |
| A20 | RC6 | The tracker issue was created after commits existed; early history could only be linked by rewriting it | binding Tracker; issue before code |
| A21 | — | A list extracted into a named group left one consumer holding a stale literal copy | gate Coupling map |
| A22 | RC6 | ~100 review and requirement IDs rode into doc comments, test names and filenames; two reached runtime evidence strings | DG-LEAK |
| A23 | RC3 | Some parallel branches merged direct to trunk, others through review; nobody had decided | binding Merge policy required |
| A24 | RC2 | A framework choice recorded as undecided was resolved inline with a third option nobody had named | Open forks; DG-REGISTRY-ROW on TBD |
| A25 | RC7 | Prior art found what builds a CLI, never what tests it; zero CLI tests for months | gate Prior art builds-or-tests column |
| A26 | RC1 | A tool marked "adopt" in a decision log was never installed or wired | gate Prior art verdict + binding Gate commands |
| A27 | RC7 | The first fit-for-purpose tool was adopted without comparing alternatives | gate Prior art ≥2 rows |
| A28 | RC5 | Six gate dimensions reported green from one lint-and-test command for hundreds of steps | phase `tier2` keys required |
| A29 | RC1 | A checker confirmed broken was correctly deferred, and the exact error class it catches shipped in the same window | gate Assumptions; re-run the check |
| A30 | RC1 | A register labelled "generated" had no generator and drifted for eleven merges | DG-REGISTRY-STALE / MISSING |
| A31 | RC1 | "One tool" was an invariant in prose; a second CLI sat in the tree for the whole build | ADR Verification required |
| A32 | RC5 | A README status section grew one paragraph per milestone and went a dozen steps stale | DG-CURRENCY |
| A33 | RC5 | Nothing outside the per-unit gate ever looked at accumulated state | computed status; no ceremony file |
| A34 | RC7 | A local CI mirror matched command names but not the runner OS; BSD and GNU flags diverged | binding target OS |
| A35 | RC3 | A git hook's environment leaked into a nested git call and corrupted a sibling worktree | parallel-agents checklist |
| A36 | RC1 | A machine-verified tag was typed before the verification ran; the number was wrong | Verification ledger dated rows |
| A37 | RC1 | An inherited "there is no clean way" claim licensed a hook bypass; the claim was false | DG-ASSUMPTION |
| A38 | RC3 | The next free ID was read from trunk while an open PR already held it | DG-HWM |
| A39 | RC2 | A narrow instruction returned as a rewrite plus three improvements | checkpoint protocol |
| A40 | RC3 | A tidy-up swept a stood-down peer's worktrees and ledger rows | parallel-agents checklist |
| A41 | RC1 | Every mechanical gate green while thirty prose claims were false | DG-CURRENCY; ledger |
| A42 | RC3 | An agent took its identity from a memory file and handed over the wrong half of the work | identity read live |
| A43 | RC1 | The orchestrator's "verified" brief had two counts off by one; agents were told not to re-derive | orchestration.md brief rule |
| A44 | RC1 | A doc gate scoped to one subdirectory never saw the root files that held the errors | explicit `docs` globs; DG-SECTION match |
| A45 | RC1 | A documented capability was recommended for deletion; its machinery already existed, unused | gate Prior art searched inward |
| A46 | RC1 | Exact-byte patches transcribed into a ledger no longer applied by apply time | record location + claim, not bytes |
| A47 | RC4 | A verifier killed by a content filter was counted as one errored agent among eleven | SKIPPED is never a pass |
| A48 | RC1 | A peer's stated constraint reshaped the work; nobody ran the one command that refuted it | primary source before adopting |
| A49 | RC6 | Do/Verify bullets grew on a requirement, a second untracked copy of the job | DG-BANNED (doc-set rule) |
| A50 | RC5 | Outstanding work lived in a "Known Gaps" list no ID could cite | DG-BANNED |
| A51 | RC6 | Externally blocked work was marked closed and forgotten | `parked` needs a `decision_ref` |
| A52 | RC4 | Finished work lived only in an agent's return value; the container was reclaimed | resilient-workflow artefact-first |
| A53 | RC2 | A prerequisite only a human could run was deferred to the end; the run built on it anyway | resilient-workflow `doneWhen` prerequisites |
| A54 | RC3 | The live orchestrator edited the shared checkout while another agent switched its branch | parallel-agents checklist |
| A55 | — | A rename retrofit rewrote dated historical narration to the new name | doc-architecture.md |
| A56 | RC2 | "Why isn't this fixed?" was answered with a pushed fix nobody asked for | checkpoint protocol |
| A57 | RC2 | A found error was written up for "whoever owns it" and stayed broken | checkpoint protocol: fix or ask |
| A58 | RC1 | Three hardcoded stage counts in three files, none matching the registry | DG-BANNED for literal counts |
| A59 | RC2 | Five misplaced checks got a patch offer; the registry that prevents the sixth surfaced only when asked | checkpoint protocol: redesign first |
| A60 | RC1 | Two independent agents agreed a valid construct was a fatal syntax error | run the oracle regardless of votes |
| A61 | RC1 | A markdown table was reshaped after checking other docs; two production modules parsed it | repo-wide grep before reshaping |
| A62 | RC1 | A whole-file substring check was satisfied by an unrelated mention elsewhere in the file | DG-ADOPTION scoped to the function |
| A63 | RC1 | A "still open" claim citing a file was reconfirmed for weeks against the wrong file | DG-CURRENCY |
| A64 | RC3 | A rendered doc kept sections whose JSON source a merge had dropped, four times in one session | DG-REGISTRY-ORPHAN |
| A65 | RC7 | A whole-tree docs lint failed every PR on debt none of them introduced | `--staged` / `--scope-to-diff` |
| A66 | RC5 | A gate log and a milestone registry built to fix A28 and A33 held 353 identical green rows and zero rows respectively | computed status; no evidence file |
| A67 | RC1 | An ADR said a gate was superseded; eighteen stages still called it months later | DG-TOMBSTONE; ADR Verification |
| A68 | RC1 | Two fields fully covered separately, never in the combination that failed | Testing guide names field pairs |
| A69 | RC6 | A commit called itself a stopgap and named the real fix; nothing tracked it | stopgap wording needs a tracked ID |
| A70 | RC7 | New code copied the nearest file, which used the superseded pattern | gate Prior art checks decisions; DG-TOMBSTONE |
