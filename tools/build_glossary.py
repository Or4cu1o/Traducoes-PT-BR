#!/usr/bin/env python3
"""Gera tools/glossary.json a partir da tabela de glossário do CONTRIBUTING.md.

A fonte da verdade é a seção 5 do CONTRIBUTING.md, com linhas no formato
`| EN | PT-BR | Nota |`. Linhas cuja Nota seja "não traduzir" são ignoradas
(o termo deve permanecer em inglês).

Uso:
    python3 tools/build_glossary.py           # escreve tools/glossary.json
    python3 tools/build_glossary.py --check   # falha se o json estiver defasado
"""
from __future__ import annotations
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CONTRIBUTING = os.path.join(REPO, "CONTRIBUTING.md")
GLOSSARY_JSON = os.path.join(HERE, "glossary.json")

_ROW = re.compile(r"^\|(?P<en>[^|]+)\|(?P<pt>[^|]+)\|(?P<note>[^|]*)\|\s*$")
_SKIP_NOTE = {"não traduzir", "nao traduzir"}


def load_glossary(path: str = CONTRIBUTING) -> dict:
    """Retorna {termo_en_minusculo: termo_ptBR} a partir do CONTRIBUTING.md."""
    out: dict = {}
    in_section_5 = False
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.startswith("## "):
                in_section_5 = stripped.startswith("## 5")
                continue
            if not in_section_5:
                continue
            m = _ROW.match(line.rstrip("\n"))
            if not m:
                continue
            en = m.group("en").strip()
            pt = m.group("pt").strip()
            note = m.group("note").strip().lower()
            if not en or en.lower() == "en" or set(en) <= {"-", ":"}:
                continue
            if note in _SKIP_NOTE or not pt:
                continue
            out[en.lower()] = pt
    return out


def main(argv: list) -> int:
    glossary = load_glossary()
    if not glossary:
        print("ERRO: nenhuma entrada de glossário encontrada em CONTRIBUTING.md",
              file=sys.stderr)
        return 1
    payload = json.dumps(glossary, ensure_ascii=False, indent=2,
                         sort_keys=True) + "\n"
    if "--check" in argv:
        current = ""
        if os.path.exists(GLOSSARY_JSON):
            with open(GLOSSARY_JSON, "r", encoding="utf-8") as fh:
                current = fh.read()
        if current != payload:
            print("ERRO: tools/glossary.json está defasado. Rode "
                  "`python3 tools/build_glossary.py`.", file=sys.stderr)
            return 1
        print(f"OK: glossário com {len(glossary)} entradas, json atualizado.")
        return 0
    with open(GLOSSARY_JSON, "w", encoding="utf-8") as fh:
        fh.write(payload)
    print(f"Escrito {GLOSSARY_JSON} com {len(glossary)} entradas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
