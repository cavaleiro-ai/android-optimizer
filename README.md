# Android Optimizer

Skill para o [Claude Code](https://claude.com/claude-code) que guia a otimização de celulares e tablets Android pelo USB, passo a passo. Antes de qualquer alteração, ela pergunta até onde você quer ir. Se quiser, ela também melhora a câmera e instala um emulador de PlayStation 1 com o seu jogo.

*English summary: a Claude Code skill that optimizes Android devices over ADB and Fastboot. It always asks how far to go first, from reversible tweaks to custom ROMs and overclocking, and it measures every change. It can also scan and improve the camera (camera app, video bitrate, filters, hidden driver features, long-exposure night shots) and set up a PlayStation 1 emulator with a game file you provide. Docs are in Portuguese; the skill replies in your language.*

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

## Câmera (opcional)

Peça, por exemplo:

```text
a câmera do meu celular está ruim, conectei no usb, melhora ela e coloca filtros
```

A skill então:

1. **Faz uma varredura só de leitura** (`camera-scan.sh`): versão do driver, nível do Camera2, sensores, resoluções, modos de câmera lenta, limites de bitrate do vídeo, apps de câmera e bibliotecas do fabricante.
2. **Mede o ponto de partida** numa cena fixa: tempo até a foto salva, exposição, ruído, nitidez, qualidade JPEG real e bitrate real do vídeo.
3. **Aplica o que a medição justificar**, no nível que você escolher:

| Nível | Exemplos | Root |
|---|---|---|
| Só apps | [Open Camera](https://opencamera.org.uk/) conferido no F-Droid e configurado por arquivo, HDR e DRO por software, panorama, bitrate de vídeo no máximo do encoder, filtros ao vivo e na galeria | Não |
| Recursos ocultos | Propriedades do driver ligadas pelo ADB, testadas uma a uma e desfeitas no fim, como a exposição longa dos Motorola | Não, em alguns aparelhos |
| Sistema | Bibliotecas de recursos que faltam, só depois de provar que o driver as usa | Sim |

4. **Confere de verdade**: câmera lenta é medida contando quadros contra o relógio, e cada recurso só entra se mudar a foto.

**Você decide o que instalar.** A skill não instala GCam modificada nem bibliotecas de outros aparelhos sem explicar o risco e pedir confirmação, e nunca as publica. As fotos de teste ficam só no computador de trabalho e são apagadas no fim.

O procedimento está em [`camera.md`](skills/android-optimizer/references/camera.md), e o registro do teste real, no [estudo de caso da câmera](docs/estudo-de-caso-camera-moto-g-2014.md).

## O que ela não faz

- Não contorna bloqueio de tela, trava FRP, MDM ou bloqueio de operadora.
- Não altera IMEI.
- Não garante recuperar fotos apagadas.
- Não baixa jogos nem BIOS.
- Não instala GCam modificada nem bibliotecas de câmera de outros aparelhos sem pedir, e não as distribui.
- Não funciona em iPhone.

## Resultado no caso real

Em um Moto G 2014 com 1 GB de RAM, passando do Android 6.0 ao LineageOS 17.1 (Android 10):

| App | Antes | Depois |
|---|---|---|
| WhatsApp | 3,46 s | 2,05 s |
| Telegram | 4,64 s | 3,36 s |

Na câmera do mesmo aparelho, medido numa cena com pouca luz:

| Item | Antes | Depois |
|---|---|---|
| Bitrate real do vídeo 720p | 9,9 Mbps | 20,0 Mbps |
| Foto noturna (exposição forçada de 850 ms) | brilho 21,7, ruído 0,85 | brilho 58,1, ruído 0,74 |
| HDR | travava no app original | 23 s, com 63% menos área estourada |
| Filtros | 8 efeitos ao vivo e 9 na galeria | mais 16 na galeria Fossify |

Na foto comum, o novo app e o original saíram iguais, porque o processamento é do próprio chip. A câmera lenta de 90 e 120 fps anunciada pela ROM não era real, e as bibliotecas de CAC, ChromaFlash, OptiZoom e UbiFocus carregaram, mas o driver da Motorola nunca as usa: foram removidas.

No mesmo aparelho, Resident Evil 3 rodou a **59,89 FPS** em uma cena 3D automática, com o maior intervalo entre quadros em 33 ms, usando a BIOS simulada. O som e o jogo sob controle de uma pessoa ainda não foram avaliados.

Esses números não valem como promessa para outros aparelhos. Os registros completos, inclusive das falhas, estão nos estudos de caso da [otimização](docs/estudo-de-caso-moto-g-2014.md), do [emulador](docs/estudo-de-caso-ps1-moto-g-2014.md) e da [câmera](docs/estudo-de-caso-camera-moto-g-2014.md).

## Estado do projeto

**A skill foi executada de verdade em um único aparelho**, o Moto G 2014. Em outras marcas, as instruções ainda não foram testadas, e as regras de desbloqueio mudam com frequência. Por isso, a skill pede que o agente pesquise o modelo exato. Root, modo desempenho e overclock também não foram executados. O emulador só foi testado em 32 bits e com um jogo. A parte da câmera só foi testada nesse aparelho, com driver Qualcomm HAL1. Aparelhos com Camera2 completo e drivers mais novos não foram testados.

Testes em outros aparelhos e correções são bem-vindos: abra uma issue com o modelo, a versão do Android e o que aconteceu, sem dados pessoais.

## Requisitos

- [Claude Code](https://claude.com/claude-code).
- Windows, macOS ou Linux.
- Cabo USB de dados.
- Android com depuração USB ativada.
- Para o emulador: Python 3 no computador, para os scripts auxiliares, e o arquivo do seu jogo.
- Para a câmera: Python 3. A análise profunda das bibliotecas usa também `capstone` e `pyelftools`, que a skill instala num ambiente virtual se você aceitar.

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
  scripts/                   Diagnóstico, medição, câmera e auxiliares do emulador
  evals/                     Testes de comportamento da skill
install.ps1 / install.sh     Instaladores
```

## Privacidade

A skill orienta o agente a não exibir serial, IMEI, contas ou senhas. Mesmo assim, o que você digita na conversa vai para o histórico do Claude Code e para o modelo. Evite colar senhas: digite-as no aparelho.

O `.gitignore` bloqueia imagens, ROMs, APKs, jogos, saves e o registro de cada otimização. Revise o que for enviar antes de fazer `git push`, principalmente em forks.

## Licença

[MIT](LICENSE). Esta skill não distribui ROMs, recoveries, apps, emuladores, jogos, BIOS nem bibliotecas de câmera: cada um tem a própria licença, e o que for instalado deve vir da fonte original.

Android é marca da Google LLC, e PlayStation é marca da Sony Interactive Entertainment. Este projeto não tem vínculo com Google, Anthropic, Motorola, Qualcomm, LineageOS, TWRP, Sony, Capcom, libretro, Open Camera, Fossify ou F-Droid.
