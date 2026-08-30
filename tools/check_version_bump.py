#!/usr/bin/env python3
"""Compara `info.json.version` entre uma revisão antiga e a árvore atual.

Regras:
  - versão nunca pode retroceder  -> erro (exit 1)
  - versão igual                  -> nada a lançar (changed=false, exit 0)
  - versão maior (ou 1ª release)  -> lançar (changed=true, exit 0)

A revisão antiga é lida com `git show <ref>:info.json`. Se o ref for vazio,
só zeros (branch recém-criado) ou não tiver info.json, trata como 1ª release.

Uso:
    python3 tools/check_version_bump.py                       # compara com HEAD^
    python3 tools/check_version_bump.py --old-ref <sha>
    python3 tools/check_version_bump.py --old-ref <sha> --github-output
"""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
INFO = os.path.join(REPO, "info.json")

_ZERO_RE = re.compile(r"^0*$")


def parse_version(raw: str) -> tuple:
    """'2.0.0' -> (2, 0, 0, 0). Aceita 2 a 4 componentes numéricos."""
    parts = raw.strip().split(".")
    if not (2 <= len(parts) <= 4) or not all(p.isdigit() for p in parts):
        raise ValueError(f"versão inválida: {raw!r}")
    nums = [int(p) for p in parts]
    while len(nums) < 4:
        nums.append(0)
    return tuple(nums)


def version_from_text(text: str) -> str:
    return json.loads(text)["version"]


def current_version() -> str:
    with open(INFO, "r", encoding="utf-8") as fh:
        return version_from_text(fh.read())


def old_version(ref: str):
    if not ref or _ZERO_RE.match(ref):
        return None
    try:
        out = subprocess.run(
            ["git", "-C", REPO, "show", f"{ref}:info.json"],
            capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None
    try:
        return version_from_text(out)
    except (json.JSONDecodeError, KeyError):
        return None


def emit_github_output(changed: bool, version: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"changed={'true' if changed else 'false'}\n")
        fh.write(f"version={version}\n")


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old-ref", default="HEAD^",
                    help="revisão git da versão anterior (default: HEAD^)")
    ap.add_argument("--github-output", action="store_true",
                    help="grava changed= e version= em $GITHUB_OUTPUT")
    args = ap.parse_args(argv)

    new_raw = current_version()
    new = parse_version(new_raw)
    old_raw = old_version(args.old_ref)

    if old_raw is None:
        print(f"sem versão anterior em {args.old_ref!r}; tratando como 1ª release "
              f"({new_raw}).")
        if args.github_output:
            emit_github_output(True, new_raw)
        return 0

    old = parse_version(old_raw)
    if new < old:
        print(f"ERRO: retrocesso de versão proibido: {old_raw} -> {new_raw}",
              file=sys.stderr)
        if args.github_output:
            emit_github_output(False, new_raw)
        return 1
    if new == old:
        print(f"versão inalterada ({new_raw}); nada a lançar.")
        if args.github_output:
            emit_github_output(False, new_raw)
        return 0

    print(f"bump de versão: {old_raw} -> {new_raw}")
    if args.github_output:
        emit_github_output(True, new_raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
