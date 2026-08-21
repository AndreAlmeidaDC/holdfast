# Governance

*[Português abaixo / Portuguese below](#governança)*

## Scope

Holdfast is a coordination pattern for long, partitionable agent work. It does not
process personal data, does not call any external API, and does not depend on any
third-party package. Everything it touches is local: a state file, per-unit output
files, and a handoff document, all written to a directory the user chooses.

## Declared capabilities

Unlike some of this author's other skills, Holdfast does execute code as part of normal
use — the workflow instructs the agent to run `holdfast-init.sh`, `holdfast-status.sh`
and `holdfast-collect.py` via the shell. This is declared honestly in `metadata.json`:

- `subprocess`: **true** — the skill causes shell and Python execution by design.
- `network_egress`: **false** — nothing in the skill or its scripts reaches the network.
- `dependency_install`: **false** — Python standard library only, no package to install.

If a future change adds a network call, a new dependency, or any capability not covered
above, `metadata.json` must be updated before the change is published. A stale
capability declaration is worse than none.

## Update policy

Updates are surfaced to the user at the start of a meaningful use, following
`references/version-check.md`. The skill never updates itself silently and never
overwrites local changes without explicit approval.

## What contributions should preserve

- **State lives in files, not in conversation.** Any change that makes resumption depend
  on chat history or runtime memory works against the skill's entire purpose.
- **No network, no third-party dependency**, unless the user explicitly decides the
  tradeoff is worth it and the declared capabilities are updated accordingly.
- **Honesty about untested runtimes.** Claims about runtimes other than Claude Code are
  inference from documented behavior, not first-hand verification. Keep that distinction
  visible; do not upgrade an inference to a fact.

## Author

André Almeida — github.com/AndreAlmeidaDC

---

## Governança

*[English above](#governance)*

## Escopo

Holdfast é um padrão de coordenação para trabalho de agente longo e particionável. Ele
não processa dado pessoal, não chama nenhuma API externa, e não depende de pacote de
terceiro. Tudo o que ele toca é local: um arquivo de estado, arquivos de saída por
unidade, e um documento de handoff, todos escritos num diretório que o usuário escolhe.

## Capacidades declaradas

Diferente de outras skills deste autor, o Holdfast executa código como parte do uso
normal — o fluxo instrui o agente a rodar `holdfast-init.sh`, `holdfast-status.sh` e
`holdfast-collect.py` via shell. Isso está declarado com honestidade no `metadata.json`:

- `subprocess`: **true** — a skill causa execução de shell e Python por design.
- `network_egress`: **false** — nada na skill ou nos scripts acessa rede.
- `dependency_install`: **false** — só biblioteca padrão do Python, nenhum pacote a instalar.

Se uma mudança futura adicionar chamada de rede, dependência nova, ou qualquer capacidade
não coberta acima, o `metadata.json` precisa ser atualizado antes de a mudança ser
publicada. Uma declaração de capacidade desatualizada é pior que nenhuma.

## Política de atualização

Atualizações são apresentadas ao usuário no início de um uso significativo, conforme
`references/version-check.md`. A skill nunca se atualiza silenciosamente nem sobrescreve
mudanças locais sem aprovação explícita.

## O que contribuições devem preservar

- **Estado vive em arquivo, não na conversa.** Qualquer mudança que faça a retomada
  depender do histórico do chat ou da memória do runtime vai contra o propósito inteiro
  da skill.
- **Sem rede, sem dependência de terceiro**, a menos que o usuário decida explicitamente
  que a troca vale a pena e as capacidades declaradas sejam atualizadas de acordo.
- **Honestidade sobre runtimes não testados.** Afirmações sobre runtimes além do Claude
  Code são inferência a partir de comportamento documentado, não verificação de primeira
  mão. Manter essa distinção visível; não promover inferência a fato.

## Autor

André Almeida — github.com/AndreAlmeidaDC
