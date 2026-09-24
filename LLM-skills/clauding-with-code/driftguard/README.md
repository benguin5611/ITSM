# driftguard

Reference-integrity and drift checks for a markdown doc set, plus generated registries whose status
is computed (from a merged PR, a cited test's exit code, a CVSS vector), never hand-typed. Stdlib
only, Python 3.11+.

## Install

Stack-agnostic — driftguard checks a markdown doc set, not the target project's own language, so it
runs via `uvx` rather than being added to that project's `pyproject.toml`:

```sh
uvx --from "driftguard @ git+https://github.com/benguin5611/ITSM#subdirectory=LLM-skills/clauding-with-code/driftguard" driftguard check
```

Pin a version for reproducibility by appending a tag or commit to the repo URL (e.g. `ITSM@<sha>`) —
the pin `templates/binding.md` records for the docs gate.

## Configure

One `driftguard.toml`; every path in it is relative to the file. Start from `examples/light.toml`
(a single-file spec) or `examples/doc-set.toml` (per-file ADRs, a sliced build plan, registries).
Keys: `docs`, `exclude`, `plugins`, `[[id_classes]]`, `[[templates]]`, `[[banned]]`, `[leaks]`,
`[[adoption]]`, `[currency]`, `[[registries]]`.

## Run

```sh
driftguard check                       # every configured check
driftguard check --staged              # add diff-scoped checks against the index
driftguard check --diff-base origin/main --scope-to-diff
driftguard write build_plan            # render one registry from its JSON source
```

Output is one line per finding, `path:line: CHECK-ID: message`, or `--json`. Exit 0 clean, 1
findings, 2 misconfiguration. A check that cannot run (no `gh`, no `cvss`) is reported as
`SKIPPED`, never as a pass.

## Checks

Always on: `DG-DANGLING`, `DG-DUPLICATE`, `DG-TOMBSTONE`, `DG-LEGACY`, `DG-FILENAME`, `DG-EARS`,
`DG-SECTION`, `DG-ROW-INCOMPLETE`, `DG-ASSUMPTION`, `DG-BANNED`. With config: `DG-LEAK`,
`DG-ADOPTION`, `DG-HWM`, `DG-CURRENCY` (diff mode), `DG-UNDISCHARGED`, `DG-REGISTRY-*`.

## Extend

`plugins = ["tools.driftguard_checks"]` names a module (importable from the config's directory)
exposing `CHECKS: list[Callable[[Context], list[Finding]]]`. Each runs after the built-ins with
the same `Context` (`cfg`, `docs`, `diff`, `skipped`).

## Hook

```sh
# .githooks/pre-commit — enable once with: git config core.hooksPath .githooks
uvx --from "driftguard @ git+https://github.com/benguin5611/ITSM#subdirectory=LLM-skills/clauding-with-code/driftguard" driftguard check --staged || exit 1
```
