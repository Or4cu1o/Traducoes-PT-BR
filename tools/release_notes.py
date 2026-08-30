#!/usr/bin/env python3
"""Gera as notas de uma GitHub Release a partir do bloco do `changelog.txt`.

O `changelog.txt` segue o formato do Factorio (indentação de 2/4/6 espaços);
colado cru no GitHub isso vira bloco de código. Este script converte para
Markdown no padrão das releases anteriores do projeto: uma frase de abertura,
seções com cabeçalho `# <emoji> <Título>` e listas com `- `.

Uso:
    python3 tools/release_notes.py                 # versão de info.json
    python3 tools/release_notes.py 2.0.0
    python3 tools/release_notes.py 2.0.0 --intro "Lançamento especial ..."
"""
from __future__ import annotations
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from changelog_extract import extract  # noqa: E402

# Categoria canônica do changelog -> cabeçalho no padrão das releases.
HEADERS = {
    "Features": "# 🆕 Novidades",
    "Minor Features": "# ✨ Melhorias",
    "Changes": "# 📝 Alterações",
    "Bugfixes": "# 🐛 Correções",
    "Locale": "# 🌐 Traduções",
    "Info": "# 🏷️ Notas",
}


def current_version() -> str:
    with open(os.path.join(REPO, "info.json"), "r", encoding="utf-8") as fh:
        return json.load(fh)["version"]


def render(body_lines: list, version: str, tag_prefix: str, intro: str) -> str:
    out = [intro or f"Lançamento da `{tag_prefix}{version}`.", ""]
    for raw in body_lines:
        stripped = raw.strip()
        if not stripped:
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        # Cabeçalho de categoria: 2 espaços de indentação, termina com ":".
        if indent <= 2 and stripped.endswith(":") and not stripped.startswith("-"):
            name = stripped[:-1].strip()
            out += ["", HEADERS.get(name, f"# {name}"), ""]
            continue
        if stripped.startswith("- "):
            text = stripped[2:].strip()
            # 4 espaços -> item raiz; 6+ -> subitem.
            prefix = "- " if indent <= 4 else "  - "
            out.append(f"{prefix}{text}")
            continue
        # Linha de continuação/livre dentro de uma categoria.
        out.append(f"  {stripped}" if indent >= 6 else stripped)
    # normaliza linhas em branco consecutivas
    norm = []
    for line in out:
        if line == "" and norm and norm[-1] == "":
            continue
        norm.append(line)
    return "\n".join(norm).strip() + "\n"


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version", nargs="?", default=None)
    ap.add_argument("--file", default=os.path.join(REPO, "changelog.txt"))
    ap.add_argument("--intro", default=None, help="frase de abertura personalizada")
    ap.add_argument("--tag-prefix", default="V", help="prefixo da tag (default: V)")
    args = ap.parse_args(argv)

    version = args.version or current_version()
    with open(args.file, "r", encoding="utf-8") as fh:
        body = extract(fh.read(), version)
    if body is None:
        print(f"bloco 'Version: {version}' não encontrado em {args.file}",
              file=sys.stderr)
        return 1
    sys.stdout.write(render(body, version, args.tag_prefix, args.intro))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
