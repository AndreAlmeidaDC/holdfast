# holdfast

**🇬🇧 [English](#english) · 🇧🇷 [Português](#português)**

---

## English

**A skill for running long agent work so that an interruption costs almost nothing.**

Partitions a big job into independent units, makes each worker write its output to disk *before* it reports back, and keeps a state file any cold session can read. When the usage limit hits — and it will — you lose the units in flight, not the run.

---

### Why "holdfast"

A holdfast is the root-like structure that anchors kelp to rock. It is not a root — it absorbs nothing, it only grips. Surge comes through, the blade whips around, water leaves. The grip stays.

That is the property this skill is about. It does not make long runs faster, cheaper, or less likely to be interrupted. It makes the finished part **stay finished** when the interruption comes.

The word is also an old command — *hold fast* — and a woodworking clamp, and in both senses it means the same thing: keep your grip on what you already have.

The alternative names all missed something. *Checkpoint* is generic and describes a mechanism instead of a property. *Ratchet* is close — progress that only moves one way — but already means something else in developer tooling. *Blackbox* survives the crash but implies opacity, and this skill's whole point is that state is legible from outside. Holdfast is a thing that grips and does not let go, which is exactly the promise.

---

### Install

```bash
git clone https://github.com/AndreAlmeidaDC/holdfast.git ~/.claude/skills/holdfast
```

Or copy the directory into wherever your runtime loads skills from.

**Dependencies:** a filesystem, a shell, Python 3 (standard library only), and some way to run work in parallel. No packages, no SDK, no network.

That poverty is deliberate. Dependencies are things that break when you resume on a different machine six weeks later.

---

### Quick start

```bash
bash ~/.claude/skills/holdfast/scripts/holdfast-init.sh my-run ./work
```

Then:

1. Edit `work/STATE.json` — declare your units
2. Edit `work/PROTOCOL.md` — declare the shared contract workers follow
3. Dispatch wave 1 using `assets/dispatch-prompt.template.md`
4. `bash work/status.sh` — anytime, from any session, with no context

---

### The idea in one line

> The unit of durability must be smaller than the unit of dispatch, and state belongs in files rather than in any runtime's memory.

Everything else follows. A worker that flushed its findings has banked them. A worker holding forty minutes of work in context to write one beautiful summary loses all of it when the limit hits.

---

### The six practices

| # | Practice | Why |
|---|---|---|
| 1 | Partition before dispatching | without a written unit list there is no resumption, only restart |
| 2 | One protocol file, not N copies in prompts | short prompts, auditable contract, no drift across workers |
| 3 | Workers flush early and often | the rule that does the actual saving |
| 4 | Status command that works from zero context | turns "where were we?" into one command |
| 5 | Waves with checkpoints between them | the only moment nothing is in flight is the cheapest place to consolidate |
| 6 | Partial completion is first-class | reading the material is the expensive part; if it is recorded, resuming is cheap |

Detail in `SKILL.md`.

---

### Runtime support — read this before running it anywhere but Claude Code

The pattern is runtime-agnostic *by construction*: state lives in files, and files do not care which agent reads them. What differs is narrow — **how work is dispatched, and how completion is detected**.

That second one splits runtimes into two families, and the difference is the whole story.

#### Push runtimes — works as written

**Claude Code · Codex · Antigravity**

The runtime notifies the orchestrator when a child finishes. Dispatch, do something else, get told.

- **Claude Code** — reference implementation, no adaptation needed. One caveat: a notification can fire more than once for the same task, and an early one may carry a truncated report while work is still in flight. If a report contradicts the disk, believe the disk.
- **Codex** — worker instructions live in `[agents]` config rather than inline. Point the agent definition at `PROTOCOL.md` and pass only unit id, scope and output path per call — which is what practice 2 wants anyway.
- **Antigravity** — minimal changes. Confirm background subagents survive the parent moving on before using wide waves.

#### Cursor — works, with a shape change

Background agents are oriented toward autonomous branch work rather than orchestrated fan-out, and completion surfaces in the agent panel rather than to a driving agent. Two viable shapes: one agent per unit with a human reading `status.sh` between waves, or a single agent looping units in series. The second loses parallelism and keeps every durability property. Start there if unsure.

#### Pull runtimes — needs real adaptation

**OpenClaw · Hermes · Gemini-CLI · Kimi CLI · Grok CLI · pi**

These have **no in-process subagent**. Delegation is a shell command launching a child process, and **nothing tells you when it finishes**. Four things change:

**The status script stops being a convenience and becomes infrastructure.** In push runtimes it answers "where are we?" for a human. Here it answers "is the wave done?" for the orchestrator, on a loop, every few seconds. It has to be cheap and correct.

**You need a wait loop with a deadline between waves.** A child that dies silently produces no signal at all — without a deadline the orchestrator waits forever on a corpse. Pattern in `references/runtimes.md`.

**Detect completion from files, not processes.** A live PID does not mean progress; a dead PID does not mean failure, since the worker may have flushed everything and exited cleanly a second before you looked. Workers already write status into their files — read that, and the detection stays consistent with the resume logic.

**Flush harder.** With no notification, the gap between "worker died" and "orchestrator noticed" is your poll interval. Where a push runtime is fine flushing every ten items, flush every three to five here.

**Hermes specifically** has a self-improvement loop that can rewrite its own skills between runs. Pin `PROTOCOL.md` and treat it as read-only input, or a long run ends with different units measured against silently different contracts — which corrupts the aggregate with no error appearing anywhere.

#### Any other runtime

Answer three questions and the rest transfers unchanged:

1. **How do I start N things in parallel?** If you cannot, run units in series. You lose throughput and keep every durability property — a legitimate configuration, not a degraded one.
2. **How do I know something finished?** No push signal means you are in the pull family: add the wait loop, shorten flush intervals.
3. **Can a child outlive the parent's turn?** If not, waves must fit inside one turn. Narrow waves, flush often.

---

### What is in the box

```
holdfast/
├── SKILL.md                          the skill itself
├── README.md                         this file
├── CHANGELOG.md                      version history
├── GOVERNANCE.md                     scope, declared capabilities, update policy
├── CONTRIBUTING.md                   how to contribute and what to validate
├── metadata.json                     declared capabilities and update policy
├── scripts/
│   ├── holdfast-init.sh              scaffold a run
│   ├── holdfast-status.sh            state from disk, zero context
│   ├── holdfast-collect.py           aggregate, deterministic, re-runnable
│   └── validate_skill.py             local structural validation (for contributors)
├── references/
│   ├── runtimes.md                   per-runtime adaptation, in detail
│   └── version-check.md              origin version check protocol
└── assets/
    ├── PROTOCOL.template.md          the shared worker contract
    ├── HANDOFF.template.md           resumable handoff
    ├── dispatch-prompt.template.md   worker prompt shape
    └── resume-prompt.template.md     resume prompt shape
```

---

### Updates

This skill checks its origin repository at the start of a meaningful use and tells you if
a newer version exists, with a summary of what changed. It never updates itself silently
and never overwrites local changes without asking first. See `references/version-check.md`
and `GOVERNANCE.md` for the full protocol.

---

### Honest limits

**Exercised only on Claude Code.** Everything written about other runtimes is inference from their documented dispatch model — sound reasoning, not evidence.

**No eval suite yet.** The test worth running is blunt: start a wave, kill the session mid-flight, measure what survives. That single experiment is worth more than any amount of reading, and it is the same standard this skill would want applied to anything else claiming resilience.

**It does not make anything faster.** Coordination costs real overhead. What you buy is that the finished part stays finished.

**It does not prevent interruptions.** It changes what they cost.

---

### Three failure modes it will not save you from

**Trusting the report over the disk.** Notifications routinely understate what was saved — a worker reporting that it is "now writing" may already have flushed most of its output. Triaging from notifications redoes completed work. **Always check the disk.**

**A parser that silently drops rows.** Formatting variation in worker output — a bold marker, an extra space — makes a strict regex skip rows without erroring. The rows sit in the file and never reach the aggregate. Have workers emit their own counts so the totals can be cross-checked; `collect.py` does this and warns on mismatch.

**Contaminating workers with unverified context.** Passing your own conclusions as established fact turns independent workers into echoes, and one upstream error propagates into every unit. Pass context as *hypothesis to test* and ask what they refuted. Workers correcting each other — and occasionally retracting their own findings after checking a primary source — is what keeps the aggregate honest.

---

### License

MIT.

---
---

## Português

**Uma skill para rodar trabalho longo de agente de forma que uma interrupção custe quase nada.**

Divide um job grande em unidades independentes, faz cada worker escrever a saída em disco *antes* de reportar, e mantém um arquivo de estado que qualquer sessão fria consegue ler. Quando o limite de uso bater — e vai bater — você perde as unidades em andamento, não o run inteiro.

---

### Por que "holdfast"

Um holdfast é a estrutura, parecida com raiz, que ancora a alga (kelp) na rocha. Não é uma raiz — não absorve nada, só segura. A onda passa, a lâmina da alga chicoteia, a água vai embora. O agarre fica.

Essa é a propriedade sobre a qual esta skill trata. Ela não torna runs longos mais rápidos, mais baratos, ou menos sujeitos a interrupção. Ela faz a parte já pronta **continuar pronta** quando a interrupção chega.

A palavra também é um comando antigo — *hold fast*, "segure firme" — e uma morsa de marcenaria, e nos dois sentidos significa a mesma coisa: manter o agarre sobre o que você já tem.

Os nomes alternativos deixavam algo escapar. *Checkpoint* é genérico e descreve um mecanismo em vez de uma propriedade. *Ratchet* (catraca) chega perto — progresso que só anda numa direção — mas já significa outra coisa no vocabulário de ferramentas de desenvolvimento. *Blackbox* sobrevive ao crash mas sugere opacidade, e o ponto inteiro desta skill é que o estado é legível de fora. Holdfast é uma coisa que agarra e não solta, que é exatamente a promessa.

---

### Instalação

```bash
git clone https://github.com/AndreAlmeidaDC/holdfast.git ~/.claude/skills/holdfast
```

Ou copie o diretório para onde quer que o seu runtime carregue skills.

**Dependências:** um sistema de arquivos, um shell, Python 3 (só biblioteca padrão), e alguma forma de rodar trabalho em paralelo. Sem pacote, sem SDK, sem rede.

Essa pobreza é deliberada. Dependência é o tipo de coisa que quebra quando você retoma numa máquina diferente seis semanas depois.

---

### Começo rápido

```bash
bash ~/.claude/skills/holdfast/scripts/holdfast-init.sh meu-run ./work
```

Depois:

1. Edite `work/STATE.json` — declare suas unidades
2. Edite `work/PROTOCOL.md` — declare o contrato compartilhado que os workers seguem
3. Despache a wave 1 usando `assets/dispatch-prompt.template.md`
4. `bash work/status.sh` — a qualquer momento, de qualquer sessão, sem contexto nenhum

---

### A ideia em uma linha

> A unidade de durabilidade tem que ser menor que a unidade de despacho, e o estado pertence a arquivos, não à memória de nenhum runtime.

Todo o resto decorre disso. Um worker que salvou suas descobertas já as garantiu. Um worker que segura quarenta minutos de trabalho no contexto pra escrever um resumo bonito no final perde tudo quando o limite bate.

---

### As seis práticas

| # | Prática | Por quê |
|---|---|---|
| 1 | Particionar antes de despachar | sem uma lista de unidades escrita não há retomada, só reinício |
| 2 | Um arquivo de protocolo, não N cópias nos prompts | prompts curtos, contrato auditável, sem divergência entre workers |
| 3 | Workers salvam cedo e com frequência | a regra que efetivamente salva o trabalho |
| 4 | Comando de status que funciona a partir de contexto zero | transforma "onde a gente parou?" num único comando |
| 5 | Waves com checkpoints entre elas | o único momento em que nada está em andamento é o mais barato para consolidar |
| 6 | Conclusão parcial é cidadã de primeira classe | ler o material é a parte cara; se está registrado, retomar é barato |

Detalhes em `SKILL.md`.

---

### Suporte por runtime — leia antes de rodar em qualquer lugar que não seja o Claude Code

O padrão é agnóstico de runtime *por construção*: o estado vive em arquivos, e arquivo não liga para qual agente o lê. O que muda é estreito — **como o trabalho é despachado, e como a conclusão é detectada**.

Esse segundo ponto divide os runtimes em duas famílias, e a diferença é a história inteira.

#### Runtimes push — funciona como está escrito

**Claude Code · Codex · Antigravity**

O runtime notifica o orquestrador quando um filho termina. Despacha, faz outra coisa, é avisado.

- **Claude Code** — implementação de referência, sem adaptação necessária. Uma ressalva: uma notificação pode disparar mais de uma vez para a mesma tarefa, e uma delas, mais cedo, pode carregar um relatório truncado enquanto o trabalho ainda está em andamento. Se um relatório contradiz o disco, acredite no disco.
- **Codex** — as instruções do worker vivem na configuração `[agents]` em vez de inline. Aponte a definição do agente para `PROTOCOL.md` e passe só id da unidade, escopo e caminho de saída por chamada — que é o que a prática 2 já pede de qualquer forma.
- **Antigravity** — mudanças mínimas. Confirme que subagentes em background sobrevivem ao pai seguindo em frente antes de usar waves largas.

#### Cursor — funciona, com mudança de formato

Agentes em background são orientados a trabalho autônomo em branch em vez de fan-out orquestrado, e a conclusão aparece no painel do agente em vez de ser avisada a um agente condutor. Dois formatos viáveis: um agente por unidade com um humano lendo `status.sh` entre waves, ou um único agente iterando unidades em série. O segundo perde paralelismo e mantém toda propriedade de durabilidade. Comece por aí se estiver em dúvida.

#### Runtimes pull — precisa de adaptação de verdade

**OpenClaw · Hermes · Gemini-CLI · Kimi CLI · Grok CLI · pi**

Estes **não têm subagente in-process**. Delegação é um comando de shell lançando um processo filho, e **nada te avisa quando termina**. Quatro coisas mudam:

**O script de status deixa de ser conveniência e vira infraestrutura.** Em runtimes push ele responde "onde estamos?" para um humano. Aqui ele responde "a wave terminou?" para o orquestrador, em loop, a cada poucos segundos. Precisa ser barato e correto.

**Você precisa de um loop de espera com prazo entre waves.** Um filho que morre silenciosamente não produz sinal nenhum — sem um prazo, o orquestrador espera para sempre por um cadáver. Padrão em `references/runtimes.md`.

**Detecte conclusão pelos arquivos, não pelos processos.** Um PID vivo não significa progresso; um PID morto não significa falha, já que o worker pode ter salvado tudo e saído limpo um segundo antes de você olhar. Os workers já escrevem status nos próprios arquivos — leia isso, e a detecção fica consistente com a lógica de retomada.

**Salve com mais frequência.** Sem notificação, o intervalo entre "worker morreu" e "orquestrador percebeu" é o seu intervalo de polling. Onde um runtime push está bem salvando a cada dez itens, aqui salve a cada três a cinco.

**O Hermes especificamente** tem um loop de auto-aperfeiçoamento que pode reescrever as próprias skills entre runs. Trave o `PROTOCOL.md` e trate-o como entrada somente leitura, ou um run longo termina com unidades diferentes medidas contra contratos silenciosamente diferentes — o que corrompe o agregado sem nenhum erro aparecer em lugar nenhum.

#### Qualquer outro runtime

Responda três perguntas e o resto se transfere sem mudança:

1. **Como eu inicio N coisas em paralelo?** Se não consegue, rode as unidades em série. Você perde throughput e mantém toda propriedade de durabilidade — uma configuração legítima, não degradada.
2. **Como eu sei que algo terminou?** Sem sinal push significa que você está na família pull: adicione o loop de espera, encurte os intervalos de salvamento.
3. **Um filho pode sobreviver ao turno do pai?** Se não, as waves precisam caber dentro de um turno. Waves estreitas, salve com frequência.

---

### O que tem na caixa

```
holdfast/
├── SKILL.md                          a skill em si
├── README.md                         este arquivo
├── CHANGELOG.md                      histórico de versões
├── GOVERNANCE.md                     escopo, capacidades declaradas, política de atualização
├── CONTRIBUTING.md                   como contribuir e o que validar
├── metadata.json                     capacidades declaradas e política de atualização
├── scripts/
│   ├── holdfast-init.sh              monta a estrutura de um run
│   ├── holdfast-status.sh            estado a partir do disco, contexto zero
│   ├── holdfast-collect.py           agrega, determinístico, re-executável
│   └── validate_skill.py             validação estrutural local (para contribuidores)
├── references/
│   ├── runtimes.md                   adaptação por runtime, em detalhe
│   └── version-check.md              protocolo de verificação de versão de origem
└── assets/
    ├── PROTOCOL.template.md          o contrato compartilhado do worker
    ├── HANDOFF.template.md           handoff retomável
    ├── dispatch-prompt.template.md   formato do prompt de worker
    └── resume-prompt.template.md     formato do prompt de retomada
```

---

### Atualizações

Esta skill verifica o repositório de origem no início de um uso significativo e avisa se
existe uma versão mais nova, com um resumo do que mudou. Ela nunca se atualiza
silenciosamente nem sobrescreve mudanças locais sem perguntar antes. Veja
`references/version-check.md` e `GOVERNANCE.md` para o protocolo completo.

---

### Limites honestos

**Exercitado só no Claude Code.** Tudo que está escrito sobre outros runtimes é inferência a partir do modelo de despacho documentado deles — raciocínio sólido, não evidência.

**Ainda sem suíte de avaliação.** O teste que vale a pena rodar é direto: inicie uma wave, mate a sessão no meio, meça o que sobrevive. Esse experimento único vale mais que qualquer quantidade de leitura, e é o mesmo padrão que esta skill gostaria de ver aplicado a qualquer outra coisa que alegue resiliência.

**Não torna nada mais rápido.** Coordenação custa overhead real. O que você compra é que a parte pronta continua pronta.

**Não previne interrupções.** Muda o que elas custam.

---

### Três modos de falha dos quais ela não vai te salvar

**Confiar no relatório em vez do disco.** Notificações rotineiramente subestimam o que foi salvo — um worker relatando que está "agora escrevendo" pode já ter salvo a maior parte da saída. Triar a partir de notificações refaz trabalho já concluído. **Sempre confira o disco.**

**Um parser que descarta linhas silenciosamente.** Variação de formatação na saída do worker — um marcador em negrito, um espaço extra — faz um regex estrito pular linhas sem dar erro. As linhas ficam no arquivo e nunca chegam ao agregado. Faça os workers emitirem sua própria contagem para que os totais possam ser cruzados; o `collect.py` faz isso e avisa em caso de divergência.

**Contaminar workers com contexto não verificado.** Passar suas próprias conclusões como fato estabelecido transforma workers independentes em ecos, e um erro na origem se propaga para cada unidade. Passe contexto como *hipótese a testar* e pergunte o que eles refutaram. Workers se corrigindo entre si — e às vezes retratando o próprio achado depois de checar a fonte primária — é o que mantém o agregado honesto.

---

### Licença

MIT.
