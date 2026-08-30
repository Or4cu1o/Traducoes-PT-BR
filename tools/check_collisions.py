#!/usr/bin/env python3
"""Detecta colisões de chave entre os .cfg de locale/pt-BR.

O Factorio funde TODOS os .cfg de um mod por `[secao]` + chave, sem olhar o
nome do arquivo; em caso de repetição, o último arquivo carregado vence. Se
dois arquivos definem a MESMA `[secao] chave` com textos DIFERENTES, o
resultado in-game depende da ordem de carga (alfabética pelo nome do arquivo)
e pode não ser o esperado.

Este script lista essas colisões divergentes. Colisões em que todos os
arquivos concordam no texto são inofensivas e só aparecem em modo detalhado.

Baseline: `tools/collisions-baseline.txt` guarda as assinaturas
`[secao] chave` já conhecidas/aceitas. `--check` só falha se surgir uma
colisão divergente fora da baseline (uso no CI).

Uso:
    python3 tools/check_collisions.py                 # relatório completo
    python3 tools/check_collisions.py --quiet         # só o resumo
    python3 tools/check_collisions.py --check         # CI: falha em colisão nova
    python3 tools/check_collisions.py --update-baseline
"""
from __future__ import annotations
import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LOCALE_DIR = os.path.join(REPO, "locale", "pt-BR")
BASELINE = os.path.join(HERE, "collisions-baseline.txt")

SECTION_RE = re.compile(r"^\[([^\]]+)\]$")


def parse_cfg(path: str) -> dict:
    """Retorna {(secao, chave): valor}. Chave antes da 1ª seção -> secao ''."""
    out: dict = {}
    section = ""
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#") or s.startswith(";"):
                continue
            m = SECTION_RE.match(s)
            if m:
                section = m.group(1)
                continue
            if "=" in s:
                key, val = s.split("=", 1)
                out[(section, key.strip())] = val
    return out


def collect() -> dict:
    """{(secao, chave): {arquivo: valor}} para chaves em >= 2 arquivos."""
    seen: dict = {}
    for path in sorted(glob.glob(os.path.join(LOCALE_DIR, "*.cfg"))):
        name = os.path.basename(path)
        for (section, key), val in parse_cfg(path).items():
            seen.setdefault((section, key), {})[name] = val
    return {k: v for k, v in seen.items() if len(v) >= 2}


def signature(section: str, key: str) -> str:
    return f"[{section}] {key}"


def divergent(shared: dict) -> dict:
    """Subconjunto em que os arquivos NÃO concordam no texto (após strip)."""
    out = {}
    for (section, key), by_file in shared.items():
        values = {v.strip() for v in by_file.values()}
        if len(values) >= 2:
            out[(section, key)] = by_file
    return out


def load_baseline() -> set:
    if not os.path.exists(BASELINE):
        return set()
    out = set()
    with open(BASELINE, "r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s and not s.startswith("#"):
                out.add(s)
    return out


def write_baseline(signatures: list) -> None:
    header = (
        "# Colisões de chave cross-file já conhecidas em locale/pt-BR.\n"
        "# Gerado por tools/check_collisions.py --update-baseline.\n"
        "# Uma assinatura '[secao] chave' por linha.\n"
    )
    with open(BASELINE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header)
        for sig in sorted(signatures):
            fh.write(sig + "\n")


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true", help="só o resumo")
    ap.add_argument("--check", action="store_true",
                    help="falha (exit 1) se houver colisão divergente fora da baseline")
    ap.add_argument("--update-baseline", action="store_true",
                    help="regrava tools/collisions-baseline.txt com o estado atual")
    args = ap.parse_args(argv)

    if not os.path.isdir(LOCALE_DIR):
        print(f"ERRO: {LOCALE_DIR} não encontrado", file=sys.stderr)
        return 2

    shared = collect()
    div = divergent(shared)
    identical = len(shared) - len(div)
    sig_to_key = {signature(sec, key): (sec, key) for (sec, key) in div}
    sigs = set(sig_to_key)

    if args.update_baseline:
        write_baseline(sorted(sigs))
        print(f"baseline regravada: {len(sigs)} colisão(ões) divergente(s) "
              f"em {os.path.relpath(BASELINE, REPO)}")
        return 0

    baseline = load_baseline()
    new = sorted(sigs - baseline)
    resolved = sorted(baseline - sigs)

    if args.check:
        for sig in new:
            print(f"COLISÃO NOVA  {sig}")
            for name, val in sorted(div[sig_to_key[sig]].items()):
                print(f"    {name}: {val}")
        if resolved:
            print(f"\n({len(resolved)} colisão(ões) da baseline já não divergem — "
                  f"rode --update-baseline para limpar)")
        print(f"\n{len(sigs)} colisão(ões) divergente(s) | "
              f"{len(new)} nova(s) fora da baseline")
        return 1 if new else 0

    if not args.quiet:
        for sig in sorted(sigs):
            print(sig)
            for name, val in sorted(div[sig_to_key[sig]].items()):
                print(f"    {name}: {val}")
            print()

    print(f"{len(shared)} chave(s) em >=2 arquivos | "
          f"{len(div)} divergente(s) | {identical} idêntica(s) (inofensivas)")
    if baseline:
        print(f"baseline: {len(baseline)} | novas fora da baseline: {len(new)} | "
              f"resolvidas: {len(resolved)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
