---
description: Roda a suíte de validação completa do pacote (locale, glossário, changelog, colisões, empacotamento)
---

Execute, na raiz do repositório, e reporte o resultado de cada passo:

```bash
python3 tools/build_glossary.py --check
python3 tools/validate_locale.py --strict locale/pt-BR
python3 tools/validate_locale.py --standalone --source-mods ../_source_mods locale/pt-BR
python3 -m json.tool info.json > /dev/null && echo "info.json: JSON válido"
python3 tools/check_changelog.py changelog.txt
python3 tools/gen_mods_table.py --check
python3 tools/check_collisions.py --check
python3 tools/build_release.py --target 2.0 --dry-run
```

Regras de leitura do resultado:

- **Qualquer erro (`erro(s)` > 0, exit ≠ 0) bloqueia o commit.**
- Avisos tolerados (não são regressão): os 3 de `gui-unifyer.cfg` sobre
  "inserter", e os ~32 do `--standalone` da classe "`[mod-name]` /
  `[mod-description]` ausente no template en".
- `check_collisions --check` só pode falhar com colisão **nova** fora de
  `tools/collisions-baseline.txt`. Se a colisão for legítima e revista,
  rode `python3 tools/check_collisions.py --update-baseline` e cite no commit.
- Se `../_source_mods` não existir, o passo `--standalone` avisa e segue —
  não é erro, mas registre que a checagem de cobertura ficou parcial.

Ao final, diga em uma linha se está **pronto para commit** ou **o que falta**.
