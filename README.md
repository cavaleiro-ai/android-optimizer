# Android Optimizer

Skill para o [Claude Code](https://claude.com/claude-code) que guia a otimização de celulares e tablets Android pelo USB, passo a passo. Antes de qualquer alteração, ela pergunta até onde você quer ir. Se quiser, ela também instala um emulador de PlayStation 1 com o seu jogo.

*English summary: a Claude Code skill that optimizes Android devices over ADB and Fastboot. It always asks how far to go first, from reversible tweaks to custom ROMs and overclocking, and it measures every change. It can also set up a PlayStation 1 emulator with a game file you provide. Docs are in Portuguese; the skill replies in your language.*

> **Aviso:** desbloquear o bootloader, trocar o sistema, fazer root ou overclock pode apagar seus dados, anular a garantia, afetar apps de banco e deixar o aparelho sem ligar. Use por sua conta e risco, e só em aparelhos seus ou com autorização do dono.

## Até onde ela pode ir

A skill pergunta o objetivo, o nível e se você quer trocar o sistema. Você escolhe:

| Nível | O que faz | Risco |
|---|---|---|
| **A. Diagnóstico** | Só lê e mede | Nenhum |
| **B. Ajustes reversíveis** | Animações, buscas em segundo plano e compilação de apps | Baixo |
| **C. Limpeza de apps** | Desativa ou remove apps dispensáveis | Baixo a médio |
| **D. Root e modo desempenho** | Mantém as frequências oficiais mais altas | Alto |
| **E. Kernel e overclock** | Experimental | Muito alto |
| **Troca de sistema** (opcional) | Bootloader, recovery e ROM. Apaga tudo | Alto |

Ela nunca apaga dados sem uma confirmação específica, usa sempre o serial do aparelho, salva os valores antigos, compara antes e depois, e desfaz o que não ajudar.

## Emulador de PS1 (opcional)

Peça, por exemplo:

```text
instala um emulador de ps1 no meu celular, o jogo está em C:\Jogos\meu-jogo.zip
```

A skill então:

1. Escolhe a versão do [RetroArch](https://www.retroarch.com/) e do núcleo para o processador do seu aparelho.
2. Confere o tipo real do arquivo do jogo, extrai e envia ao celular, comparando o checksum.
3. Instala o núcleo [PCSX ReARMed](https://docs.libretro.com/library/pcsx_rearmed/) e deixa a tela deitada.
4. Coloca o jogo em uma lista no menu do RetroArch.
5. Mede os quadros em uma cena 3D e só altera opções se houver lentidão medida.
6. Diz o que você precisa testar, como som, controles e save.

**Você fornece o jogo.** A skill não baixa jogos nem BIOS, e não indica sites para isso. Use cópias suas ou jogos de distribuição livre. Não é preciso root, desbloqueio nem troca de sistema.

O procedimento está em [`ps1-emulator.md`](skills/android-optimizer/references/ps1-emulator.md), e o registro do teste real, no [estudo de caso do PS1](docs/estudo-de-caso-ps1-moto-g-2014.md).

## O que ela não faz

- Não contorna bloqueio de tela, trava FRP, MDM ou bloqueio de operadora.
- Não altera IMEI.
- Não garante recuperar fotos apagadas.
- Não baixa jogos nem BIOS.
- Não funciona em iPhone.

## Resultado no caso real

Em um Moto G 2014 com 1 GB de RAM, passando do Android 6.0 ao LineageOS 17.1 (Android 10):

| App | Antes | Depois |
|---|---|---|
| WhatsApp | 3,46 s | 2,05 s |
| Telegram | 4,64 s | 3,36 s |

No mesmo aparelho, Resident Evil 3 rodou a **59,89 FPS** em uma cena 3D automática, com o maior intervalo entre quadros em 33 ms, usando a BIOS simulada. O som e o jogo sob controle de uma pessoa ainda não foram avaliados.

Esses números não valem como promessa para outros aparelhos. Os registros completos, inclusive das falhas, estão nos estudos de caso da [otimização](docs/estudo-de-caso-moto-g-2014.md) e do [emulador](docs/estudo-de-caso-ps1-moto-g-2014.md).

## Estado do projeto

**A skill foi executada de verdade em um único aparelho**, o Moto G 2014. Em outras marcas, as instruções ainda não foram testadas, e as regras de desbloqueio mudam com frequência. Por isso, a skill pede que o agente pesquise o modelo exato. Root, modo desempenho e overclock também não foram executados. O emulador só foi testado em 32 bits e com um jogo.

Testes em outros aparelhos e correções são bem-vindos: abra uma issue com o modelo, a versão do Android e o que aconteceu, sem dados pessoais.

## Requisitos

- [Claude Code](https://claude.com/claude-code).
- Windows, macOS ou Linux.
- Cabo USB de dados.
- Android com depuração USB ativada.
- Para o emulador: Python 3 no computador, para os scripts auxiliares, e o arquivo do seu jogo.

A skill ajuda a instalar o ADB e o Fastboot.

## Instalação

**Como plugin**, dentro do Claude Code:

```text
/plugin marketplace add cavaleiro-ai/android-optimizer
/plugin install android-optimizer@android-optimizer
```

**Com os scripts**, a partir da pasta do repositório:

```powershell
# Windows
.\install.ps1
```

```bash
# macOS / Linux
sh install.sh
```

**Manual:** copie `skills/android-optimizer` para `~/.claude/skills/`.

## Como usar

Conecte o aparelho, abra o Claude Code e peça, por exemplo:

```text
meu celular android está lento, conectei no usb, otimiza ele
```

Ou chame diretamente: `/android-optimizer`.

## Estrutura

```text
.claude-plugin/              Manifesto do plugin e do marketplace
docs/                        Estudos de caso completos
skills/android-optimizer/
  SKILL.md                   Fluxo principal
  references/                Instruções de cada etapa, inclusive o emulador
  scripts/                   Diagnóstico, medição e auxiliares do emulador
  evals/                     Testes de comportamento da skill
install.ps1 / install.sh     Instaladores
```

## Privacidade

A skill orienta o agente a não exibir serial, IMEI, contas ou senhas. Mesmo assim, o que você digita na conversa vai para o histórico do Claude Code e para o modelo. Evite colar senhas: digite-as no aparelho.

O `.gitignore` bloqueia imagens, ROMs, APKs, jogos, saves e o registro de cada otimização. Revise o que for enviar antes de fazer `git push`, principalmente em forks.

## Licença

[MIT](LICENSE). Esta skill não distribui ROMs, recoveries, apps, emuladores, jogos nem BIOS: cada um tem a própria licença, e o que for instalado deve vir da fonte original.

Android é marca da Google LLC, e PlayStation é marca da Sony Interactive Entertainment. Este projeto não tem vínculo com Google, Anthropic, Motorola, LineageOS, TWRP, Sony, Capcom ou libretro.
