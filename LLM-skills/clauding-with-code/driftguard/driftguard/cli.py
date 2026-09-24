"""`driftguard check` / `driftguard write NAME`. Exit 0 clean, 1 findings, 2 misconfiguration."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

from . import Context, Finding, __version__, checks, registry
from . import scan as scanmod
from .config import ConfigError, load

USAGE_ERROR = 2


def _plugins(cfg) -> list:
    fns = []
    if not cfg.plugins:
        return fns
    sys.path.insert(0, str(cfg.root))
    for name in cfg.plugins:
        try:
            mod = importlib.import_module(name)
        except Exception as e:  # noqa: BLE001
            raise ConfigError(f"plugin {name!r} failed to import: {e}") from None
        found = getattr(mod, "CHECKS", None)
        if not isinstance(found, (list, tuple)):
            raise ConfigError(f"plugin {name!r} has no CHECKS list")
        fns += list(found)
    return fns


def build_context(args) -> Context:
    cfg = load(args.config)
    diff = None
    if getattr(args, "staged", False) or getattr(args, "diff_base", None):
        diff = scanmod.Diff(cfg, staged=args.staged, base=args.diff_base)
    return Context(cfg=cfg, docs=scanmod.scan(cfg), diff=diff)


def do_check(args) -> int:
    ctx = build_context(args)
    only = set(args.only.split(",")) if args.only else None
    findings: list[Finding] = []
    for fn in [*checks.BUILTIN, *_plugins(ctx.cfg)]:
        findings += fn(ctx)
    findings += registry.run_registries(ctx)
    if only:
        findings = [f for f in findings if f.check in only]
    if args.scope_to_diff:
        if ctx.diff is None:
            raise ConfigError("--scope-to-diff needs --staged or --diff-base")
        changed = ctx.diff.changed_files
        findings = [f for f in findings if f.path in changed]
    findings = sorted(set(findings))
    if args.json:
        print(json.dumps({"ok": not findings, "findings": [f.__dict__ for f in findings],
                          "skipped": ctx.skipped, "defs": {k: len(v) for k, v in ctx.docs.defs.items()}}))
    else:
        for f in findings:
            print(f)
        for s in ctx.skipped:
            print(f"SKIPPED: {s}", file=sys.stderr)
        if not findings:
            print(f"driftguard: clean ({sum(len(v) for v in ctx.docs.defs.values())} ids, {len(ctx.docs.files)} files)")
    return 1 if findings else 0


def do_write(args) -> int:
    ctx = build_context(args)
    names = {r["name"] for r in ctx.cfg.registries}
    if args.name not in names:
        raise ConfigError(f"no registry named {args.name!r}; configured: {sorted(names) or 'none'}")
    findings = sorted(set(registry.run_registries(ctx, write_name=args.name)))
    for f in findings:
        print(f)
    for s in ctx.skipped:
        print(f"SKIPPED: {s}", file=sys.stderr)
    if not findings:
        print(f"driftguard: wrote {args.name}")
    return 1 if findings else 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="driftguard", description=__doc__)
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="run every configured check")
    c.add_argument("--config", default="driftguard.toml")
    c.add_argument("--json", action="store_true")
    c.add_argument("--staged", action="store_true", help="diff mode: index vs HEAD")
    c.add_argument("--diff-base", metavar="REF", help="diff mode: REF..HEAD")
    c.add_argument("--scope-to-diff", action="store_true", help="report only findings in changed files")
    c.add_argument("--only", metavar="CHECK,...", help="comma-separated CHECK-IDs to report")
    c.set_defaults(fn=do_check)
    w = sub.add_parser("write", help="render and write one generated registry")
    w.add_argument("name")
    w.add_argument("--config", default="driftguard.toml")
    w.set_defaults(fn=do_write, staged=False, diff_base=None)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.fn(args)
    except (ConfigError, scanmod.DiffError) as e:
        print(f"driftguard: {e}", file=sys.stderr)
        return USAGE_ERROR


if __name__ == "__main__":
    sys.exit(main())
