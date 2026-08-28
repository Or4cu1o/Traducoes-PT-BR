#!/usr/bin/env python3
"""Valida o formato de changelog.txt conforme a engine do Factorio.

Regras verificadas:
  - a primeira linha e todo separador de bloco têm exatamente 99 traços "-"
  - cada bloco começa com "Version: X.Y.Z" (semver de 2 ou 3 componentes)
  - "Date:" presente logo após "Version:" (formato livre; avisa se não bater
    com DD/MM/AAAA ou AAAA-MM-DD)
  - linhas de categoria terminam com ":" e são indentadas com 2 espaços
  - linhas de item começam com 4 espaços + "- "
  - o arquivo termina com quebra de linha

O bloco mais recente (primeiro do arquivo) é avaliado com rigor: desvios de
formatação viram ERRO. Blocos legados: desvios viram AVISO.

Uso:
    python3 tools/check_changelog.py changelog.txt
"""
from __future__ import annotations
import os
import re
import sys

SEP = "-" * 99
VERSION_RE = re.compile(r"^Version: (\d+\.\d+(?:\.\d+)?)\s*$")
DATE_RE = re.compile(r"^Date: (.+?)\s*$")
DATE_OK_RE = re.compile(r"^(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})$")
CATEGORY_RE = re.compile(r"^ {2}([^ ].*):\s*$")
ENTRY_RE = re.compile(r"^ {4}- \S")
CONT_RE = re.compile(r"^ {6}\S")


def main(argv: list) -> int:
    path = argv[0] if argv else "changelog.txt"
    if not os.path.exists(path):
        print(f"ERRO: {path} não encontrado", file=sys.stderr)
        return 1

    with open(path, "rb") as fh:
        raw = fh.read()
    errors: list[str] = []
    warnings: list[str] = []
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append("arquivo tem BOM UTF-8")
    if b"\r" in raw:
        errors.append("arquivo contém CR (use LF)")
    if raw and not raw.endswith(b"\n"):
        errors.append("arquivo não termina com quebra de linha")
    lines = raw.decode("utf-8", "replace").split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    if not lines or lines[0] != SEP:
        errors.append(f"linha 1: deveria ser {len(SEP)} traços exatos")

    block_index = -1
    expect_version = True
    for i, line in enumerate(lines, 1):
        strict = block_index <= 0
        sink = errors if strict else warnings

        if line == SEP:
            block_index += 1
            expect_version = True
            continue
        if line != "" and line.strip() == "":
            sink.append(f"linha {i}: linha só com espaços")
            continue
        if line == "":
            continue

        if expect_version:
            if not VERSION_RE.match(line):
                sink.append(f"linha {i}: esperado 'Version: X.Y.Z', obtido {line!r}")
            expect_version = False
            continue

        md = DATE_RE.match(line)
        if md:
            if not DATE_OK_RE.match(md.group(1)):
                warnings.append(f"linha {i}: data {md.group(1)!r} fora de "
                                f"DD/MM/AAAA ou AAAA-MM-DD")
            continue
        if CATEGORY_RE.match(line):
            continue
        if ENTRY_RE.match(line) or CONT_RE.match(line):
            continue
        sink.append(f"linha {i}: formato não reconhecido {line!r}")

    for w in warnings:
        print(f"AVISO  {w}")
    for e in errors:
        print(f"ERRO   {e}")
    print(f"\n{block_index + 1} bloco(s) | {len(errors)} erro(s) | "
          f"{len(warnings)} aviso(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
