#!/usr/bin/env python3
"""Extrai o corpo de um bloco `Version: X.Y.Z` do changelog.txt.

Formato do Factorio: blocos separados por uma linha de 99 hifens; cada bloco
começa com `Version:` e `Date:`. Este script imprime as linhas de conteúdo
do bloco pedido (sem o separador, sem `Version:`/`Date:`), úteis como corpo
de uma GitHub Release.

Uso:
    python3 tools/changelog_extract.py 2.0.0
    python3 tools/changelog_extract.py 2.0.0 --file changelog.txt
Sai com código 1 (e nada no stdout) se o bloco não existir.
"""
from __future__ import annotations
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SEP = "-" * 99


def extract(text: str, version: str):
    lines = text.splitlines()
    want = f"Version: {version}"
    for i, line in enumerate(lines):
        if line.strip() != want:
            continue
        body = []
        j = i + 1
        while j < len(lines):
            stripped = lines[j].strip()
            if stripped.startswith(SEP) or stripped.startswith("Version:"):
                break
            if stripped.startswith("Date:"):
                j += 1
                continue
            body.append(lines[j])
            j += 1
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()
        return body
    return None


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version")
    ap.add_argument("--file", default=os.path.join(REPO, "changelog.txt"))
    args = ap.parse_args(argv)

    with open(args.file, "r", encoding="utf-8") as fh:
        body = extract(fh.read(), args.version)
    if body is None:
        print(f"bloco 'Version: {args.version}' não encontrado em {args.file}",
              file=sys.stderr)
        return 1
    print("\n".join(body))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
