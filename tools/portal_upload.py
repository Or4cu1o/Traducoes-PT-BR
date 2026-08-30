#!/usr/bin/env python3
"""Publica um .zip do mod no portal oficial do Factorio (Mod Upload API v2).

Fluxo:
  1. POST <init-url>  (Authorization: Bearer <APIKey>, campo `mod=<slug>`)
       -> { "upload_url": "https://.../upload/mod/..." }
  2. POST <upload_url>  (multipart/form-data, campo `file` = o .zip)
       -> { "success": true }

Configuração (variáveis de ambiente):
  FACTORIO_PORTAL_API_KEY   (obrigatória) — chave de API do portal
  FACTORIO_PORTAL_INIT_URL  (opcional)    — sobrescreve o endpoint de init

Uso:
  python3 tools/portal_upload.py --zip dist/slondo-ptbr_2.0.0.zip
  python3 tools/portal_upload.py --zip <z> --mod slondo-ptbr --dry-run
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_INIT_URL = "https://mods.factorio.com/api/v2/mods/releases/init"


def mod_slug() -> str:
    with open(os.path.join(REPO, "info.json"), "r", encoding="utf-8") as fh:
        return json.load(fh)["name"]


def _post(url: str, data: bytes, headers: dict) -> dict:
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"portal: HTTP {exc.code} em {url}\n{raw}")
    except urllib.error.URLError as exc:
        raise SystemExit(f"portal: falha de rede em {url}: {exc}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise SystemExit(f"portal: resposta não-JSON de {url}:\n{raw}")


def _multipart(field_name: str, filename: str, blob: bytes) -> tuple:
    boundary = f"----slondoptbr{uuid.uuid4().hex}"
    body = b"".join([
        f"--{boundary}\r\n".encode(),
        (f'Content-Disposition: form-data; name="{field_name}"; '
         f'filename="{filename}"\r\n').encode(),
        b"Content-Type: application/zip\r\n\r\n",
        blob,
        f"\r\n--{boundary}--\r\n".encode(),
    ])
    return body, f"multipart/form-data; boundary={boundary}"


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", required=True, help="caminho do .zip do mod")
    ap.add_argument("--mod", default=None,
                    help="slug do mod (default: info.json.name)")
    ap.add_argument("--init-url", default=None,
                    help="endpoint de init (default: env FACTORIO_PORTAL_INIT_URL "
                         "ou o oficial)")
    ap.add_argument("--dry-run", action="store_true",
                    help="valida entradas e sai sem chamar o portal")
    args = ap.parse_args(argv)

    zip_path = args.zip if os.path.isabs(args.zip) else os.path.join(REPO, args.zip)
    if not os.path.isfile(zip_path):
        raise SystemExit(f"arquivo não encontrado: {zip_path}")
    slug = args.mod or mod_slug()
    init_url = (args.init_url or os.environ.get("FACTORIO_PORTAL_INIT_URL")
                or DEFAULT_INIT_URL)
    key = os.environ.get("FACTORIO_PORTAL_API_KEY", "").strip()

    size_kb = os.path.getsize(zip_path) / 1024
    print(f"portal: mod={slug} zip={os.path.basename(zip_path)} "
          f"({size_kb:.1f} KiB) init={init_url}")

    if args.dry_run:
        print("dry-run: nada enviado.")
        return 0
    if not key:
        raise SystemExit("FACTORIO_PORTAL_API_KEY ausente.")

    init = _post(
        init_url,
        data=f"mod={urllib.parse.quote(slug)}".encode(),
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/x-www-form-urlencoded"},
    )
    upload_url = init.get("upload_url")
    if not upload_url:
        raise SystemExit(f"portal: init sem 'upload_url': {init}")

    with open(zip_path, "rb") as fh:
        blob = fh.read()
    body, content_type = _multipart("file", os.path.basename(zip_path), blob)
    result = _post(upload_url, data=body,
                   headers={"Authorization": f"Bearer {key}",
                            "Content-Type": content_type})
    if not result.get("success"):
        raise SystemExit(f"portal: upload falhou: {result}")

    print(f"portal: {slug} publicado com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
