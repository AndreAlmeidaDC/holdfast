# Contributing

*[Português abaixo / Portuguese below](#contribuindo)*

## How to contribute

1. Fork the repository
2. Work in a branch
3. Run `python3 scripts/validate_skill.py` before opening a PR
4. Open a pull request describing what changed and why

## Local validation before a PR

- Confirm `metadata.json` still reflects the skill's REAL capabilities. If you added a
  network call, a subprocess, or a new dependency, declare it in
  `declared_capabilities` before publishing.
- Confirm no machine-specific absolute path was introduced. Scripts are called by
  relative path from the skill root, or by resolving `SKILL` from
  `${BASH_SOURCE[0]}`, as `holdfast-init.sh` already does.
- If you touched a script, run it once end-to-end (`holdfast-init.sh`, then
  `status.sh`, then `collect.py` against a scaffolded run) before opening the PR.
  A change that looks correct in the diff can still break the shell one-liners.
- If you changed `README.md`, `GOVERNANCE.md` or `CONTRIBUTING.md`, update **both**
  language sections. A file where only one language reflects the change is worse than a
  file that stayed in one language from the start.

## What belongs where

- `SKILL.md` — the process: the six practices, the workflow, what to reach for it and
  when not to.
- `references/runtimes.md` — per-runtime adaptation. Keep the distinction between what
  is tested (Claude Code) and what is inference from documented behavior (everything
  else) explicit.
- `references/version-check.md` — the shared update protocol. Do not fork this file's
  structure without a reason; it stays consistent across this author's skills on purpose.
- `assets/*.template.md` — the shape of worker, dispatch, resume and handoff prompts.
- `scripts/` — the three utilities. Keep them dependency-free and network-free; that
  constraint is load-bearing (see `GOVERNANCE.md`).

## Principles that should not be broken

- The unit of durability stays smaller than the unit of dispatch.
- State lives in files, never only in conversation or runtime memory.
- No network call, no third-party dependency, without an explicit, documented decision.
- Claims about untested runtimes stay labeled as inference, not fact.

## Version bump

After any meaningful change, update the version in `metadata.json` and add a row to
`CHANGELOG.md`.

---

## Contribuindo

*[English above](#contributing)*

## Como contribuir

1. Faça um fork do repositório
2. Trabalhe em uma branch
3. Rode `python3 scripts/validate_skill.py` antes de abrir um PR
4. Abra um pull request explicando o que mudou e por quê

## Validação local antes do PR

- Confirme que o `metadata.json` continua refletindo as capacidades REAIS da skill. Se
  você adicionou chamada de rede, subprocess, ou dependência nova, declare em
  `declared_capabilities` antes de publicar.
- Confirme que nenhum caminho absoluto específico de máquina foi introduzido. Os scripts
  são chamados por caminho relativo a partir da raiz da skill, ou resolvendo `SKILL` a
  partir de `${BASH_SOURCE[0]}`, como o `holdfast-init.sh` já faz.
- Se você mexeu em um script, rode uma vez de ponta a ponta (`holdfast-init.sh`, depois
  `status.sh`, depois `collect.py` contra um run recém-criado) antes de abrir o PR. Uma
  mudança que parece correta no diff ainda pode quebrar os one-liners de shell.
- Se você alterou `README.md`, `GOVERNANCE.md` ou `CONTRIBUTING.md`, atualize **as duas**
  seções de idioma. Um arquivo onde só um idioma reflete a mudança é pior que um arquivo
  que ficou num idioma só desde o início.

## O que pertence a cada arquivo

- `SKILL.md` — o processo: as seis práticas, o fluxo, quando usar e quando não.
- `references/runtimes.md` — adaptação por runtime. Manter explícita a distinção entre o
  que foi testado (Claude Code) e o que é inferência a partir de comportamento
  documentado (todo o resto).
- `references/version-check.md` — o protocolo de atualização compartilhado. Não bifurcar
  a estrutura deste arquivo sem motivo; ele se mantém consistente entre as skills deste
  autor de propósito.
- `assets/*.template.md` — o formato dos prompts de worker, dispatch, resume e handoff.
- `scripts/` — os três utilitários. Mantê-los sem dependência e sem rede; essa restrição
  é estrutural (ver `GOVERNANCE.md`).

## Princípios que não devem ser quebrados

- A unidade de durabilidade fica menor que a unidade de despacho.
- Estado vive em arquivo, nunca só na conversa ou na memória do runtime.
- Nenhuma chamada de rede, nenhuma dependência de terceiro, sem uma decisão explícita e
  documentada.
- Afirmações sobre runtimes não testados permanecem rotuladas como inferência, não fato.

## Bump de versão

Depois de qualquer mudança relevante, atualize a versão no `metadata.json` e acrescente
uma linha no `CHANGELOG.md`.
