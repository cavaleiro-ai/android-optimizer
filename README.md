# Android Optimizer

Skill para o [Claude Code](https://claude.com/claude-code) que guia a otimização de celulares e tablets Android pelo USB, passo a passo. Antes de qualquer alteração, ela pergunta até onde você quer ir.

*English summary: a Claude Code skill that optimizes Android devices over ADB and Fastboot. It always asks how far to go first, from reversible tweaks to custom ROMs and overclocking, and it measures every change. Docs are in Portuguese; the skill replies in your language.*

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

## O que ela não faz

- Não contorna bloqueio de tela, trava FRP, MDM ou bloqueio de operadora.
- Não altera IMEI.
- Não garante recuperar fotos apagadas.
- Não funciona em iPhone.

## Resultado no caso real

Em um Moto G 2014 com 1 GB de RAM, passando do Android 6.0 ao LineageOS 17.1 (Android 10):

| App | Antes | Depois |
|---|---|---|
| WhatsApp | 3,46 s | 2,05 s |
| Telegram | 4,64 s | 3,36 s |

Esses números não valem como promessa para outros aparelhos. O registro completo, inclusive das falhas, está no [estudo de caso](docs/estudo-de-caso-moto-g-2014.md).

## Estado do projeto

**A skill foi executada de verdade em um único aparelho**, o Moto G 2014. Em outras marcas, as instruções ainda não foram testadas, e as regras de desbloqueio mudam com frequência. Por isso, a skill pede que o agente pesquise o modelo exato. Root, modo desempenho e overclock também não foram executados.

Testes em outros aparelhos e correções são bem-vindos: abra uma issue com o modelo, a versão do Android e o que aconteceu, sem dados pessoais.

## Requisitos

- [Claude Code](https://claude.com/claude-code).
- Windows, macOS ou Linux.
- Cabo USB de dados.
- Android com depuração USB ativada.

A skill ajuda a instalar o ADB e o Fastboot.

## Instalação

**Como plugin** (depois de publicar o repositório), dentro do Claude Code:

```text
/plugin marketplace add SEU-USUARIO/android-optimizer
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
docs/                        Estudo de caso completo
skills/android-optimizer/
  SKILL.md                   Fluxo principal
  references/                Instruções de cada etapa
  scripts/                   Diagnóstico e medição
  evals/                     Testes de comportamento da skill
install.ps1 / install.sh     Instaladores
```

## Privacidade

A skill orienta o agente a não exibir serial, IMEI, contas ou senhas. Mesmo assim, o que você digita na conversa vai para o histórico do Claude Code e para o modelo. Evite colar senhas: digite-as no aparelho.

O `.gitignore` bloqueia imagens, ROMs, APKs e o registro de cada otimização. Revise o que for enviar antes de fazer `git push`, principalmente em forks.

## Licença

[MIT](LICENSE). Esta skill não distribui ROMs, recoveries nem apps: cada um tem a própria licença e deve ser baixado da fonte original.

Android é marca da Google LLC. Este projeto não tem vínculo com Google, Anthropic, Motorola, LineageOS ou TWRP.
