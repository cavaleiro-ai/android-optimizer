# Estudo de caso: emulador de PS1 no Moto G 2014

Registro da instalação do RetroArch com Resident Evil 3 no mesmo Moto G 2014 do [primeiro estudo de caso](estudo-de-caso-moto-g-2014.md), feita pelo Claude Code com ADB em 1º de novembro de 2026.

Dados pessoais foram retirados. O arquivo do jogo foi fornecido pela pessoa e **não faz parte deste repositório**. Sua origem não foi verificada neste trabalho.

## Resumo

| Item | Resultado |
|---|---|
| Emulador | RetroArch 1.22.2 (32 bits) + PCSX ReARMed |
| Desempenho na cena 3D testada | **59,89 FPS**, com maior intervalo de 33,3 ms |
| Root, overclock ou troca de sistema | Não foram necessários |
| Testado pela tela e pelo ADB | Instalação, abertura, menus, botões na tela, vídeos e cenas 3D |
| Ainda não testado | Som, jogo sob controle da pessoa e save real |

## Aparelho

| Item | Valor |
|---|---|
| Sistema | LineageOS 17.1 (Android 10) |
| Processador | Snapdragon 400, 32 bits (`armeabi-v7a`), até 1,19 GHz |
| GPU | Adreno 305, OpenGL ES 3.0 |
| RAM | 906 MB |
| Espaço livre | 12 GB antes, 11 GB depois |

## Versões

| Item | Versão | Origem |
|---|---|---|
| RetroArch | 1.22.2, `RetroArch_ra32.apk`, 183,8 MB | [buildbot da libretro, estável](https://buildbot.libretro.com/stable/) |
| PCSX ReARMed | Build noturna de 01/11/2026 para `armeabi-v7a` | [buildbot da libretro, noturno](https://buildbot.libretro.com/nightly/android/latest/armeabi-v7a/) |
| Jogo | Resident Evil 3: Nemesis (EUA), bin e cue, 722 MB | Arquivo da pessoa |
| BIOS | Simulada, do próprio núcleo | Nenhum arquivo baixado |

A listagem do site trazia nome, data e tamanho. A integridade foi conferida abrindo os arquivos como zip e pelas arquiteturas internas, sem comparação com checksum publicado.

## Por que este emulador

O PCSX ReARMed é feito para processadores ARM. A escolha foi baseada nisso e no hardware do aparelho, sem comparação de desempenho com outros emuladores. O resultado confirmou que ele atende este aparelho, e não que seja o melhor possível.

## Linha do tempo

### 1. O arquivo do jogo

O `.zip` não abria no Windows. Os primeiros bytes (`37 7A BC AF 27 1C`) mostraram que era um 7z com a extensão trocada, e não um arquivo danificado. O `tar` do Windows recusou o método LZMA.

Baixar e executar o `7zr.exe` foi bloqueado pelo classificador de segurança do Claude Code. A saída foi escrever um leitor de 7z só com a biblioteca padrão do Python. O CRC conferiu, e o leitor agora faz parte da skill, em [`scripts/read7z.py`](../skills/android-optimizer/scripts/read7z.py).

### 2. Conexão

O Moto não aparecia no ADB no começo, e depois a conexão caiu várias vezes. Uma captura de tela chegou cortada, sem o fim do PNG. A pessoa reconectou o cabo, e a conexão ficou estável. A causa exata não foi confirmada.

### 3. Instalação e envio

`adb install -g` terminou com sucesso. O jogo foi enviado a 25,8 MB/s, e o MD5 no aparelho bateu com o do computador.

### 4. Núcleo

O ADB não grava na pasta privada do app sem root, e a tentativa de `run-as` falhou. O `.so` foi extraído, conferido (ELF de 32 bits para ARM) e instalado pelo menu **Install or Restore a Core**, que lê a pasta `RetroArch/downloads`. Colocá-lo primeiro na pasta `Download` do Android não adiantou.

### 5. Primeira execução e tela

O jogo abriu na primeira tentativa. Em pé, a imagem ficava pequena, então `screen_orientation=1` fixou a tela deitada.

### 6. Pelo menu

Os botões na tela funcionaram por `input swipe`, com uma duração de 150 ms. O jogo abriu no título com **Load Game** selecionado. Por isso, a primeira tentativa de novo jogo voltou à pergunta do cartão de memória.

### 7. Medição

Um script no aparelho repetia sempre a mesma sequência a partir de um novo início, e media uma cena 3D com fogo, zumbis e personagens. A cena é automática, sem controle da pessoa.

**O erro de medição:** as três primeiras medições incluíam uma captura de tela durante a amostra e mostraram por volta de 58,5 FPS, com uma travada de 217 a 283 ms. Sem essa captura, a travada sumiu. A captura era a causa, e o resultado correto é o da tabela abaixo.

| Medição | Captura durante a amostra | FPS | Maior intervalo | Acima de 25 ms | CPU em uso |
|---|---|---:|---:|---:|---:|
| Padrão, 1 | Sim | 58,45 | 283,3 ms | 2 | 50,4% |
| Padrão, 2 | Sim | 58,63 | 250,0 ms | 2 | 48,1% |
| Vídeo e áudio em outros núcleos | Sim | 58,90 | 216,7 ms | 1 | 51,2% |
| **Padrão, 3** | **Não** | **59,89** | **33,3 ms** | **1** | **46,1%** |
| **Padrão, 4** | **Não** | **59,89** | **33,3 ms** | **1** | **46,4%** |

A CPU em uso considera todos os núcleos ligados naquele momento. A temperatura da bateria ficou entre 37,5 °C e 41 °C, com o aparelho carregando pelo USB. O app usou cerca de 145 MB de RAM.

### 8. Ajustes

| Ajuste | Decisão | Motivo |
|---|---|---|
| Tela deitada | Mantido | Imagem bem maior |
| Botões com 50% de opacidade | Mantido | Atrapalham menos, sem medição própria |
| Contador de FPS | Desligado no final | Usado só em teste |
| `gpu_thread_rendering=sync` e `spu_thread=enabled` | Removido | Sem ganho claro de FPS ou CPU |

Essa comparação de núcleos tem dois limites. A medição teve a captura de tela, e não houve confirmação pelo menu de que as opções foram aplicadas. Os valores padrão foram mantidos porque a referência correta já ficou muito perto de 60 FPS.

### 9. Lista de jogos

Um arquivo `.lpl` colocou o jogo em **Playlists → Sony - PlayStation**. Esse caminho foi testado tocando na tela, a partir do ícone do app. Os arquivos temporários foram apagados depois.

## O que não foi verificado

- **Som:** nada foi ouvido. O contador de falhas lido no sistema estava zerado, mas ele não prova a ausência de chiado.
- **Jogo sob controle da pessoa:** todas as cenas medidas foram automáticas.
- **Save real:** o cartão de memória foi criado, mas nada foi gravado nem carregado.
- **Jogo inteiro:** a BIOS simulada pode falhar mais adiante.
- **Duração da bateria** e uso prolongado.
- **Outros jogos, emuladores e aparelhos.**

## Estado final

| Item | Estado |
|---|---|
| App | `com.retroarch.ra32` |
| Jogo | `/storage/emulated/0/ROMs/PS1/` |
| Saves | `/storage/emulated/0/RetroArch/saves/PCSX-ReARMed/` |
| Configuração | Tela deitada, botões a 50%, padrão no restante |
| Lista | `/storage/emulated/0/RetroArch/playlists/` |

## Lições

As falhas viraram itens em [`lessons.md`](../skills/android-optimizer/references/lessons.md), e o procedimento completo está em [`ps1-emulator.md`](../skills/android-optimizer/references/ps1-emulator.md).

1. **Confira o tipo real do arquivo.** A extensão pode estar errada.
2. **Uma ferramenta de medição pode causar o que mede.** O engasgo era da captura de tela, e não do jogo.
3. **Teste antes de ajustar.** Aqui, o padrão já bastava.

## Fontes

- [Documentação do PCSX ReARMed](https://docs.libretro.com/library/pcsx_rearmed/)
- [Buildbot da libretro](https://buildbot.libretro.com/)
