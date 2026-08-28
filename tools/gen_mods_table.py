#!/usr/bin/env python3
"""Regenera a tabela de mods do README.md a partir de mods.csv.

mods.csv (cabeçalho): Supported,Mod Version,Mod,Author(s),Released
  - Supported  : versão do pacote em que o mod passou a ser suportado (ex.: V1.0.4)
  - Mod Version: versão do mod tomada como base da tradução
  - Mod        : nome do mod no portal
  - Author(s)  : autoria do mod
  - Released   : data (DD/MM/AAAA) da entrada no pacote

A tabela é escrita no README.md entre os marcadores:
    <!-- MODS-TABLE:START -->
    <!-- MODS-TABLE:END -->

Uso:
    python3 tools/gen_mods_table.py            # atualiza o README.md
    python3 tools/gen_mods_table.py --check    # falha se estiver defasado
    python3 tools/gen_mods_table.py --stdout   # só imprime a tabela
"""
from __future__ import annotations
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CSV_PATH = os.path.join(REPO, "mods.csv")
README = os.path.join(REPO, "README.md")
START = "<!-- MODS-TABLE:START -->"
END = "<!-- MODS-TABLE:END -->"


def build_table() -> str:
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    out = ["| # | Mod | Autor(es) | Versão base | Desde | Data |",
           "|--:|-----|-----------|-------------|-------|------|"]
    for n, r in enumerate(sorted(rows, key=lambda r: r["Mod"].lower()), 1):
        out.append(
            f"| {n} | {r['Mod'].strip()} | {r['Author(s)'].strip()} | "
            f"{r['Mod Version'].strip()} | {r['Supported'].strip()} | "
            f"{r['Released'].strip()} |")
    out.append("")
    out.append(f"_Total: {len(rows)} mods. Gerado de `mods.csv` por "
               f"`tools/gen_mods_table.py`._")
    return "\n".join(out)


def splice(readme_text: str, table: str) -> str:
    if START not in readme_text or END not in readme_text:
        raise SystemExit(
            f"ERRO: marcadores {START} / {END} ausentes no README.md")
    pre = readme_text.split(START)[0]
    post = readme_text.split(END)[1]
    return f"{pre}{START}\n{table}\n{END}{post}"


def main(argv: list) -> int:
    table = build_table()
    if "--stdout" in argv:
        print(table)
        return 0
    with open(README, "r", encoding="utf-8") as fh:
        current = fh.read()
    updated = splice(current, table)
    if "--check" in argv:
        if current != updated:
            print("ERRO: tabela do README.md defasada. Rode "
                  "`python3 tools/gen_mods_table.py`.", file=sys.stderr)
            return 1
        print("OK: tabela do README.md sincronizada com mods.csv.")
        return 0
    with open(README, "w", encoding="utf-8") as fh:
        fh.write(updated)
    print("README.md atualizado a partir de mods.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
