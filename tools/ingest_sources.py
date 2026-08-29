#!/usr/bin/env python3
"""Ingere pt-BR dos pacotes de idioma da comunidade (Crowdin) como cópia fiel.

Fonte primária do modelo autônomo (CLAUDE.md §3 e §11): para cada chave que um
pacote nativo (AAI / LTN Language Pack) traduz em pt-BR E que existe no template
`en` correspondente do próprio pacote, o valor é copiado VERBATIM para o nosso
`locale/pt-BR/`. Onde já temos a chave com texto diferente, o texto do pacote
PREVALECE (cópia fiel — o pacote nativo tem prioridade). Marcadores são
conferidos; linha do pacote com marcador corrompido ou com contagem de `__N__`
diferente do `en` é pulada e reportada.

`boblocale` fica de fora (chaves defasadas para 2.0) — tratado por mod no
pipeline de tradução.

Uso:
    python3 tools/ingest_sources.py --report              # só relatório
    python3 tools/ingest_sources.py --apply               # grava as mudanças
    python3 tools/ingest_sources.py --apply --source-mods ../_source_mods
"""
from __future__ import annotations
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_SRC = os.path.join(os.path.dirname(REPO), "_source_mods")
LOCALE_DIR = os.path.join(REPO, "locale", "pt-BR")

SECTION_RE = re.compile(r"^\[([^\]]+)\]$")
BROKEN_MARKER_RE = re.compile(
    r"__(?: \d|\d )__|__ \d __"
    r"|__ [A-Z][A-Z_]{2,}__|__[A-Z][A-Z_]{2,} __")
BAD_NEWLINE_RE = re.compile(r"\\ n(?![A-Za-z0-9])")
NUM_MARKER_RE = re.compile(r"__\d+__")

# pacote -> { stem do arquivo no pacote : nome do nosso arquivo alvo }
# só arquivos que JÁ existem em locale/pt-BR/ são tocados; os demais são
# reportados como "arquivo novo necessário" (exigem entrada em mods.csv/info.json).
SOURCES = [
    ("AAI-Language-Pack", {
        "aai-containers": "aai-containers.cfg",
        "aai-industry": "aai-industry.cfg",
        "aai-loaders": "aai-loaders.cfg",
        "aai-programmable-structures": "aai-programmable-structures.cfg",
        "aai-programmable-vehicles": "aai-programmable-vehicles.cfg",
        "aai-zones": "aai-zones.cfg",
    }),
    ("LTN-Language-Pack", {
        "ltn-base": "ltn-base.cfg",
        "ltn-cleanup": "ltn-cleanup.cfg",
        "LTN_Combinator_Modernized": "LTN_Combinator_Modernized.cfg",
        "ltn-langpack": "ltn-langpack.cfg",
        "LtnManager": "LtnManager.cfg",
        "ltn-settings": "ltn-settings.cfg",
        "ltn-train-info": "ltn-train-info.cfg",
    }),
]


def parse_cfg(text: str) -> "list[tuple]":
    """[(section, key, value)] na ordem do arquivo."""
    out = []
    section = ""
    for raw in text.split("\n"):
        s = raw.strip()
        if not s or s.startswith("#") or s.startswith(";"):
            continue
        m = SECTION_RE.match(s)
        if m:
            section = m.group(1).strip()
            continue
        if "=" in raw:
            k, v = raw.split("=", 1)
            k = k.strip()
            if k:
                out.append((section, k, v.strip()))
    return out


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8-sig") as fh:
        return fh.read()


def marker_ok(pt_val: str, en_val: str) -> "str | None":
    """Retorna o motivo da rejeição, ou None se estiver ok."""
    if BROKEN_MARKER_RE.search(pt_val):
        return "marcador com espaço interno"
    if BAD_NEWLINE_RE.search(pt_val):
        return "'\\ n' no lugar de '\\n'"
    if sorted(NUM_MARKER_RE.findall(pt_val)) != sorted(NUM_MARKER_RE.findall(en_val)):
        return f"contagem de __N__ difere do en ({en_val!r})"
    return None


def merge_into(target_path: str, adds: dict, replaces: dict) -> str:
    """adds/replaces: {(section, key): value}. Devolve o novo conteúdo."""
    lines = read(target_path).split("\n") if os.path.exists(target_path) else []
    section = ""
    last_key_line = {}   # última linha "chave=" de cada seção (p/ inserir adds)
    for i, raw in enumerate(lines):
        s = raw.strip()
        m = SECTION_RE.match(s)
        if m:
            section = m.group(1).strip()
            last_key_line.setdefault(section, i)
            continue
        if "=" in raw and s and not s.startswith(("#", ";")):
            k = raw.split("=", 1)[0].strip()
            if k:
                last_key_line[section] = i
                if (section, k) in replaces:
                    lines[i] = f"{k}={replaces[(section, k)]}"

    by_sec: dict = {}
    for (sec, key), val in sorted(adds.items()):
        by_sec.setdefault(sec, []).append(f"{key}={val}")

    root_block = by_sec.pop("", None)   # chaves sem seção: namespace padrão

    # seções nomeadas: inserir de trás para frente para não deslocar índices
    named = [s for s in by_sec if s in last_key_line]
    for sec in sorted(named, key=lambda s: last_key_line[s], reverse=True):
        at = last_key_line[sec] + 1
        lines[at:at] = by_sec[sec]
    for sec in sorted(s for s in by_sec if s not in last_key_line):
        if lines and lines[-1].strip() != "":
            lines.append("")
        lines.append(f"[{sec}]")
        lines.extend(by_sec[sec])

    if root_block:
        if "" in last_key_line:
            at = last_key_line[""] + 1
            lines[at:at] = root_block
        else:
            lines[0:0] = root_block   # topo do arquivo, sem cabeçalho

    return "\n".join(ln.rstrip() for ln in lines).rstrip("\n") + "\n"


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="grava as mudanças")
    ap.add_argument("--report", action="store_true", help="só relatório (padrão)")
    ap.add_argument("--source-mods", default=DEFAULT_SRC)
    args = ap.parse_args(argv)
    apply = args.apply

    grand = {"add": 0, "replace": 0, "same": 0, "skip": 0}
    missing_targets = []
    for pack, mapping in SOURCES:
        pack_dir = os.path.join(args.source_mods, pack, "locale")
        for stem, target_name in sorted(mapping.items()):
            pt_path = os.path.join(pack_dir, "pt-BR", f"{stem}.cfg")
            en_path = os.path.join(pack_dir, "en", f"{stem}.cfg")
            if not os.path.exists(pt_path) or not os.path.exists(en_path):
                continue
            en_kv = {(s, k): v for s, k, v in parse_cfg(read(en_path))}
            pt_rows = parse_cfg(read(pt_path))
            target_path = os.path.join(LOCALE_DIR, target_name)
            if not os.path.exists(target_path):
                have_pt = sum(1 for s, k, v in pt_rows if v and (s, k) in en_kv)
                if have_pt:
                    missing_targets.append((target_name, pack, stem, have_pt))
                continue
            our_kv = {(s, k): v for s, k, v in parse_cfg(read(target_path))}

            adds, replaces = {}, {}
            n = {"add": 0, "replace": 0, "same": 0, "skip": 0}
            for s, k, v in pt_rows:
                if not v:
                    continue
                if (s, k) not in en_kv:
                    n["skip"] += 1
                    continue
                why = marker_ok(v, en_kv[(s, k)])
                if why:
                    print(f"  SKIP {target_name} [{s}] {k}: {why}")
                    n["skip"] += 1
                    continue
                cur = our_kv.get((s, k))
                if cur is None:
                    adds[(s, k)] = v
                    n["add"] += 1
                elif cur.strip() != v:
                    replaces[(s, k)] = v
                    n["replace"] += 1
                else:
                    n["same"] += 1
            for kk in grand:
                grand[kk] += n[kk]
            if n["add"] or n["replace"]:
                print(f"{target_name:<34} <- {pack}/{stem}: "
                      f"+{n['add']} add, ~{n['replace']} replace, "
                      f"={n['same']} iguais, {n['skip']} fora do en/marcador")
                if apply:
                    new_text = merge_into(target_path, adds, replaces)
                    with open(target_path, "w", encoding="utf-8", newline="\n") as fh:
                        fh.write(new_text)

    print(f"\nTOTAL: +{grand['add']} add, ~{grand['replace']} replace, "
          f"={grand['same']} iguais, {grand['skip']} ignoradas")
    if missing_targets:
        print("\nArquivos que precisariam ser criados (exigem mods.csv + info.json):")
        for name, pack, stem, cnt in missing_targets:
            print(f"  {name}  ({pack}/{stem}, {cnt} chaves pt-BR disponíveis)")
    if not apply:
        print("\n(relatório — use --apply para gravar)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
