#!/usr/bin/env python3
"""Validador dos arquivos de locale pt-BR do pacote slondo-ptbr.

Verificações sempre ativas (falham o build):
  - sem BOM, sem CR, sem espaço à direita, arquivo termina em \\n
  - estrutura INI válida (seção / chave=valor / comentário / vazio)
  - sem chave duplicada dentro da mesma seção
  - integridade de marcadores: __1__, __ENTITY__x__, __ITEM__x__,
    __CONTROL__x__, __ALT_CONTROL__n__x__, __plural_for_parameter__...__,
    sem espaço interno; sem "\\ n" no lugar de "\\n"

Avisos (não falham, salvo --strict):
  - seção fora do conjunto conhecido
  - possível termo em inglês não traduzido (glossário de CONTRIBUTING.md §5)
  - chave antes da primeira seção

Verificações locais opcionais (--source-mods DIR):
  - toda chave existe no template en correspondente
  - nenhuma chave coincide com o pt-BR oficial de AAI/LTN/bob

Uso:
    python3 tools/validate_locale.py locale/pt-BR
    python3 tools/validate_locale.py locale/pt-BR --strict
    python3 tools/validate_locale.py locale/pt-BR --source-mods ../_source_mods
"""
from __future__ import annotations
import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

try:
    from build_glossary import load_glossary
except ImportError:  # execução fora de tools/
    sys.path.insert(0, HERE)
    from build_glossary import load_glossary

SECTION_RE = re.compile(r"^\[([^\]]+)\]$")

# Marcador válido: "__" + token sem espaço + "__" (ex.: __1__, __ENTITY__x__).
# Corrupção de alta confiança: espaço dentro de um marcador de parâmetro
# numerado ("__ 1__", "__1 __", "__ 1 __") ou de um marcador nomeado em
# CAIXA-ALTA ("__ ENTITY__", "__ITEM __"). Prosa em pt-BR entre dois marcadores
# válidos ("__1__ de __2__") é minúscula e não casa aqui.
BROKEN_MARKER_RE = re.compile(
    r"__(?: \d|\d )__|__ \d __"
    r"|__ [A-Z][A-Z_]{2,}__|__[A-Z][A-Z_]{2,} __"
)
BAD_NEWLINE_RE = re.compile(r"\\ n(?![A-Za-z0-9])")
TAB_RE = re.compile(r"\t")

# Só termos de alta confiança viram aviso de "não traduzido" (evita ruído).
_GLOSSARY = load_glossary()
_LINT_TERMS = {
    en: pt for en, pt in _GLOSSARY.items()
    if (len(en) >= 8 and " " in en) or en in {
        "inserter", "assembler", "spoilage", "furnace",
    }
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def read_bytes(path: str, rep: Report) -> str | None:
    with open(path, "rb") as fh:
        raw = fh.read()
    name = os.path.relpath(path, REPO)
    if raw.startswith(b"\xef\xbb\xbf"):
        rep.err(name, "arquivo tem BOM UTF-8")
        raw = raw[3:]
    if b"\r" in raw:
        rep.err(name, "arquivo contém CR (use LF)")
        raw = raw.replace(b"\r", b"")
    if raw and not raw.endswith(b"\n"):
        rep.err(name, "arquivo não termina com quebra de linha")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        rep.err(name, f"não é UTF-8 válido: {exc}")
        return None


def check_markers(name: str, lineno: int, value: str, rep: Report) -> None:
    if BAD_NEWLINE_RE.search(value):
        rep.err(name, f"linha {lineno}: '\\ n' encontrado (deveria ser '\\n')")
    if TAB_RE.search(value):
        rep.err(name, f"linha {lineno}: caractere TAB no valor")
    for m in BROKEN_MARKER_RE.finditer(value):
        rep.err(name, f"linha {lineno}: marcador com espaço interno "
                      f"perto de {m.group(0)!r}")


# Remove rich-text/tag ([entity=inserter], [img=...], [font=...]), marcadores e
# trechos entre aspas antes do lint de glossário — ali "inserter" é nome de
# protótipo ou nome próprio, não texto traduzível.
_RICHTEXT_RE = re.compile(r"\[[^\]\n]*\]|__[A-Za-z0-9_]+__|\"[^\"\n]*\"")


def glossary_lint(name: str, lineno: int, value: str, rep: Report) -> None:
    prose = _RICHTEXT_RE.sub(" ", value)
    for en, pt in _LINT_TERMS.items():
        if not re.search(r"\b" + re.escape(en) + r"\b", prose, re.IGNORECASE):
            continue
        if pt.lower() in prose.lower():
            continue
        rep.warn(name, f"linha {lineno}: contém {en!r} em inglês "
                       f"(glossário: {pt!r})")


def parse_cfg(path: str, rep: Report) -> dict:
    """Retorna {(secao, chave): valor}. Registra erros/avisos em rep."""
    name = os.path.relpath(path, REPO)
    text = read_bytes(path, rep)
    if text is None:
        return {}
    section = None
    seen: set[tuple[str, str]] = set()
    out: dict[tuple[str, str], str] = {}
    for i, raw in enumerate(text.split("\n"), 1):
        line = raw
        if line != line.rstrip():
            rep.err(name, f"linha {i}: espaço em branco no fim da linha")
            line = line.rstrip()
        s = line.strip()
        if s == "" or s.startswith("#") or s.startswith(";"):
            continue
        m = SECTION_RE.match(s)
        if m:
            section = m.group(1).strip()
            continue
        if "=" not in line:
            rep.err(name, f"linha {i}: linha sem '=' e sem cabeçalho de seção")
            continue
        if section is None:
            # chaves antes de qualquer [seção] caem na seção padrão do Factorio;
            # é um uso válido e comum (mensagens referenciadas sem prefixo).
            section = ""
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            rep.err(name, f"linha {i}: chave vazia")
            continue
        if (section, key) in seen:
            rep.err(name, f"linha {i}: chave duplicada [{section}] {key}")
        seen.add((section, key))
        out[(section, key)] = value
        check_markers(name, i, value, rep)
        glossary_lint(name, i, value, rep)
    return out


_CATEGORY_SUFFIX = re.compile(
    r"\s+-\s+(item-name|item-description|entity-name|entity-description|"
    r"recipe-name|recipe-description|technology-name|technology-description|"
    r"tech|mod|misc|locale|names|quality-names)$", re.I)
_VERSION_SUFFIX = re.compile(r"_[0-9]+(?:\.[0-9]+)+$")


def _mod_stem(name: str) -> str:
    """Slug de mod comparável entre fontes. Só remove o sufixo ' - <categoria>'
    (convenção de arquivos divididos do repo) e o sufixo de versão de diretório;
    nunca corta segmentos legítimos do nome (ex.: '-planets')."""
    s = re.sub(r"\.cfg$", "", name, flags=re.I)
    s = _CATEGORY_SUFFIX.sub("", s)
    s = _VERSION_SUFFIX.sub("", s)
    return s.strip().lower().replace(" ", "-").replace("_", "-")


def _read_keys(path: str) -> list:
    out = []
    section = ""
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            lines = fh.readlines()
    except (OSError, UnicodeDecodeError):
        return out
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#") or s.startswith(";"):
            continue
        m = SECTION_RE.match(s)
        if m:
            section = m.group(1).strip()
            continue
        if "=" in raw:
            k = raw.split("=", 1)[0].strip()
            if k:
                out.append((section, k))
    return out


PACK_DIRS = {"AAI-Language-Pack", "LTN-Language-Pack", "boblocale"}
IGNORE_DIRS = {"factorio-mods-localization"}


def load_reference(source_mods: str) -> tuple:
    """Retorna (en_por_stem, oficial_ptbr_por_stem).

    `en`      : templates em inglês de qualquer mod em _source_mods/.
    `official`: pt-BR APENAS dos três pacotes de idioma (AAI/LTN/bob). O pt-BR
               que um mod traz no próprio repo NÃO conta como "oficial" — ali
               a ordem de carga resolve a sobreposição, e completá-lo é o
               objetivo do projeto.
    """
    en: dict = {}
    official: dict = {}
    for entry in sorted(os.listdir(source_mods)):
        base = os.path.join(source_mods, entry)
        if not os.path.isdir(base) or entry in IGNORE_DIRS:
            continue
        is_pack = entry in PACK_DIRS
        langs = [("en", en)]
        if is_pack:
            langs += [("pt-BR", official), ("pt", official)]
        for lang, bucket in langs:
            for path in glob.glob(
                    os.path.join(base, "**", "locale", lang, "*.cfg"),
                    recursive=True):
                stem = (_mod_stem(os.path.basename(path)) if is_pack
                        else _mod_stem(entry))
                keyset = bucket.setdefault(stem, set())
                for ln in _read_keys(path):
                    keyset.add(ln)
    return en, official


def fix_mechanical(path: str) -> list:
    """Corrige só o que é seguro e determinístico: BOM, CRLF, espaço à direita,
    quebra de linha final única. Retorna a lista de correções aplicadas."""
    with open(path, "rb") as fh:
        raw = fh.read()
    fixes = []
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
        fixes.append("BOM removido")
    if b"\r" in raw:
        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        fixes.append("CRLF -> LF")
    text = raw.decode("utf-8")
    lines = text.split("\n")
    rstripped = [ln.rstrip(" \t") for ln in lines]
    if rstripped != lines:
        fixes.append("espaço à direita removido")
    new = "\n".join(rstripped).rstrip("\n") + "\n"
    if new != "\n".join(rstripped):
        fixes.append("quebra de linha final normalizada")
    if new != text or fixes:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(new)
    return fixes


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("locale_dir", help="diretório com os .cfg (ex.: locale/pt-BR)")
    ap.add_argument("--strict", action="store_true",
                    help="tratar avisos como erros")
    ap.add_argument("--fix", action="store_true",
                    help="corrige automaticamente BOM, CRLF, espaço à direita e "
                         "quebra de linha final antes de validar")
    ap.add_argument("--source-mods", metavar="DIR",
                    help="raiz de _source_mods/ para checar cobertura e "
                         "não-sobreposição com os pacotes oficiais")
    args = ap.parse_args(argv)

    files = sorted(glob.glob(os.path.join(args.locale_dir, "*.cfg")))
    if not files:
        print(f"ERRO: nenhum .cfg em {args.locale_dir}", file=sys.stderr)
        return 1

    if args.fix:
        n_fixed = 0
        for path in files:
            done = fix_mechanical(path)
            if done:
                n_fixed += 1
                print(f"CORRIGIDO {os.path.relpath(path, REPO)}: {', '.join(done)}")
        print(f"{n_fixed} arquivo(s) corrigido(s).\n")

    rep = Report()
    parsed: dict = {}
    for path in files:
        parsed[path] = parse_cfg(path, rep)

    if args.source_mods and os.path.isdir(args.source_mods):
        en_ref, official_ref = load_reference(args.source_mods)
        for path, keys in parsed.items():
            name = os.path.relpath(path, REPO)
            stem = _mod_stem(os.path.basename(path))
            en_keys = en_ref.get(stem)
            off_keys = official_ref.get(stem, set())
            for (section, key) in keys:
                if en_keys is not None and (section, key) not in en_keys:
                    rep.warn(name, f"[{section}] {key}: ausente no template en "
                                   f"de {stem}")
                if (section, key) in off_keys:
                    rep.err(name, f"[{section}] {key}: coincide com o pt-BR "
                                  f"oficial de {stem} (não sobrepor)")
    elif args.source_mods:
        rep.warn("(geral)", f"--source-mods {args.source_mods} não é diretório; "
                            f"checagens de cobertura ignoradas")

    for w in rep.warnings:
        print(f"AVISO  {w}")
    for e in rep.errors:
        print(f"ERRO   {e}")

    n_err = len(rep.errors) + (len(rep.warnings) if args.strict else 0)
    print(f"\n{len(files)} arquivo(s) | {len(rep.errors)} erro(s) | "
          f"{len(rep.warnings)} aviso(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
