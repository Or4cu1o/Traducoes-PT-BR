#!/usr/bin/env python3
"""Empacota o mod slondo-ptbr para publicação no portal.

Mantém um único locale/ e gera uma variante por versão-alvo do jogo:
  --target 2.0  -> info.json.factorio_version = "2.0"  (foco atual)
  --target 2.1  -> info.json.factorio_version = "2.1"  (roteirizado)

O .zip contém apenas o que o portal precisa; tools/, .github/, mods.csv,
arquivos de desenvolvimento e o histórico git ficam de fora.

Uso:
    python3 tools/build_release.py --target 2.0
    python3 tools/build_release.py --target 2.1 --dry-run
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DIST = os.path.join(REPO, "dist")

# Somente estes itens entram no pacote publicado.
INCLUDE = ["info.json", "data.lua", "changelog.txt", "README.md", "LICENSE",
           "thumbnail.png", "locale"]
VALID_TARGETS = {"2.0", "2.1"}


def staged_info(target: str) -> tuple:
    with open(os.path.join(REPO, "info.json"), "r", encoding="utf-8") as fh:
        info = json.load(fh)
    info["factorio_version"] = target
    return info, info["name"], info["version"]


def iter_files() -> list:
    paths = []
    for item in INCLUDE:
        src = os.path.join(REPO, item)
        if not os.path.exists(src):
            print(f"AVISO: {item} não existe, ignorado", file=sys.stderr)
            continue
        if os.path.isfile(src):
            paths.append(item)
            continue
        for root, _dirs, names in os.walk(src):
            for n in sorted(names):
                full = os.path.join(root, n)
                paths.append(os.path.relpath(full, REPO))
    return sorted(paths)


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True, choices=sorted(VALID_TARGETS))
    ap.add_argument("--dry-run", action="store_true",
                    help="lista o conteúdo do pacote sem escrever o .zip")
    ap.add_argument("--outdir", default=DIST)
    args = ap.parse_args(argv)

    info, name, version = staged_info(args.target)
    folder = f"{name}_{version}"
    members = iter_files()

    print(f"pacote: {folder}.zip  (factorio_version={args.target})")
    for rel in members:
        print(f"  + {folder}/{rel}")
    print(f"total: {len(members)} arquivo(s)")

    if args.dry_run:
        print("dry-run: nada escrito.")
        return 0

    os.makedirs(args.outdir, exist_ok=True)
    zip_path = os.path.join(args.outdir, f"{folder}.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in members:
            if rel == "info.json":
                zf.writestr(f"{folder}/info.json",
                            json.dumps(info, ensure_ascii=False, indent=2) + "\n")
            else:
                zf.write(os.path.join(REPO, rel), f"{folder}/{rel}")
    size_kb = os.path.getsize(zip_path) / 1024
    print(f"escrito {zip_path} ({size_kb:.1f} KiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
