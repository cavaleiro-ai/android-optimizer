# Emulador de PlayStation 1

Instala o RetroArch com um núcleo de PS1, copia o jogo da pessoa, configura, mede e deixa o jogo fácil de abrir.

**Até onde isto foi testado:** instalação, configuração e medição rodaram em um único aparelho, um Moto G 2014 com Android 10, processador de 32 bits e 906 MB de RAM, usando o RetroArch 1.22.2. Som, jogo sob controle de uma pessoa e save real não foram avaliados. Em outros aparelhos, pesquise e confirme o que estiver marcado como "não testado".

**Comandos:** os exemplos usam `adb shell "..."` porque caminhos com espaços ou parênteses precisam chegar entre aspas ao aparelho. Em PowerShell, `grep` existe só dentro do `adb shell`. No Git Bash, defina `MSYS_NO_PATHCONV=1` antes do comando, senão caminhos como `/storage/...` são reescritos. Os scripts `.py` precisam de Python 3: confira com `python --version` ou `python3 --version` e, se faltar, peça permissão para instalar.

## Limites

- **Use só o arquivo que a pessoa fornecer.** Não baixe jogos nem BIOS, e não indique sites para isso. Jogos e BIOS têm direitos autorais. Se ela não tiver o arquivo, explique que pode usar a cópia de um disco próprio ou jogos independentes de distribuição livre, e instale só o emulador.
- **Não envie o jogo, a BIOS ou os saves para serviços externos** nem para o repositório.
- O emulador não exige root, desbloqueio nem troca de sistema. Não os proponha como requisito.

## Perguntas

Junte estas às que faltarem da entrevista, em uma mensagem só:

1. Onde está o arquivo do jogo no computador? Se ainda não tiver, quer instalar só o emulador?
2. Vai jogar com os botões na tela ou com controle físico?
3. Tem uma BIOS extraída do próprio console? Sem ela, o núcleo usa uma BIOS simulada.

Se o pedido for só o emulador, não ofereça otimizar o sistema mais de uma vez. Pergunte se quer otimizar também, aceite a resposta e siga.

**Sem o jogo:** faça as etapas 1, 3, 4 e 5, sem o envio de arquivos do jogo. Pare depois da etapa 5, explique que a medição depende de um jogo e diga que, com o arquivo em mãos, basta pedir para continuar pela etapa 2.

## 1. Escolher o emulador

Use o `ABI`, a RAM e a versão do Android de `scripts/diagnose.sh`:

| Aparelho | Sugestão | Situação |
|---|---|---|
| Só 32 bits (`armeabi-v7a`) | `RetroArch_ra32.apk` + PCSX ReARMed | **Testado** no Moto G 2014 |
| 64 bits (`arm64-v8a`) | `RetroArch_aarch64.apk` + PCSX ReARMed | Não testado |
| Android 11 ou mais novo | Confirme a permissão de arquivos, abaixo | Não testado |

Antes de instalar, consulte o [diretório de versões estáveis](https://buildbot.libretro.com/stable/) e pegue a mais recente. Em `<versão>/android/`, a versão 1.22.2 tinha `RetroArch.apk`, `RetroArch_aarch64.apk` e `RetroArch_ra32.apk`. Os núcleos ficam em `https://buildbot.libretro.com/nightly/android/latest/<abi>/`, como `pcsx_rearmed_libretro_android.so.zip`.

A página oficial do [PCSX ReARMed](https://docs.libretro.com/library/pcsx_rearmed/) lista os formatos e as BIOS aceitas.

## 2. Preparar o jogo

**Não confie na extensão.** No caso real, um `.zip` era um 7z, e o Windows recusava abrir. Leia os primeiros bytes:

| Início do arquivo | Tipo |
|---|---|
| `50 4B 03 04` | zip |
| `37 7A BC AF 27 1C` | 7z |
| `52 61 72 21` | rar |

Extraia para uma pasta nova e vazia, e não execute nada do que vier dentro. Use a ferramenta que a pessoa já tiver. Para 7z sem 7-Zip, `scripts/read7z.py` só usa a biblioteca padrão do Python e confere o CRC:

```text
python -I scripts/read7z.py list <arquivo>
python -I scripts/read7z.py extract <arquivo> <pasta-vazia>
```

Ele foi testado com um único arquivo (LZMA). Se o método não for aceito, peça à pessoa para instalar o 7-Zip.

Confira depois:

- **Bin e cue:** o `.cue` precisa citar o nome exato do `.bin`, e os dois ficam na mesma pasta. Abra sempre o `.cue`, nunca o `.bin`.
- **Vários discos:** crie um `.m3u` com um `.cue` por linha e abra o `.m3u`. Não testado.
- **Formatos:** a documentação lista `.bin`, `.cue`, `.img`, `.mdf`, `.pbp`, `.toc`, `.cbn`, `.m3u`, `.ccd`, `.chd`, `.iso` e `.exe`, mas não `.7z`. Extraia antes de enviar.
- **Espaço:** compare o tamanho extraído com `df -h /data` antes de enviar.

## 3. Instalar e enviar

Antes de instalar, diga o que será instalado, o tamanho (cerca de 184 MB na versão testada) e o espaço que o jogo vai ocupar, e peça a confirmação.

Baixe em uma pasta nova. Depois de baixar, compare o tamanho com a listagem e confira a integridade e as arquiteturas, abrindo o APK como zip e lendo as pastas em `lib/`. Quando o site não publicar checksum, diga que só foi possível verificar o tamanho e a integridade do arquivo.

```text
adb -s <serial> install -g RetroArch_<variante>.apk
adb -s <serial> shell "pm list packages | grep -i retroarch"
adb -s <serial> shell "mkdir -p /storage/emulated/0/ROMs/PS1"
```

Se a instalação for recusada, a tela do aparelho pode estar pedindo uma autorização, como "Instalar via USB" ou um aviso do Play Protect. Peça para a pessoa olhar a tela. Não desative proteções sem explicar e sem ela concordar.

Envie **todos** os arquivos extraídos do jogo e compare cada um com o computador. Um `.cue` pode citar vários `.bin`, enquanto `.chd` e `.pbp` vêm em um arquivo só, sem `.cue`:

```text
adb -s <serial> push "<arquivo do jogo>" /storage/emulated/0/ROMs/PS1/
adb -s <serial> shell "md5sum '/storage/emulated/0/ROMs/PS1/<arquivo do jogo>'"
```

O pacote varia por APK. No caso testado, foi `com.retroarch.ra32`, e abaixo ele aparece como `<pacote>`.

**Android 11 ou mais novo (não testado):** `install -g` não concede o acesso a todos os arquivos. Antes da primeira abertura, tente:

```text
adb -s <serial> shell appops set <pacote> MANAGE_EXTERNAL_STORAGE allow
```

Se falhar, peça para a pessoa abrir **Configurações → Apps → RetroArch → Permissões → Arquivos e mídia** e permitir o acesso. O nome do menu varia por marca.

## 4. Primeira abertura

Com a tela desbloqueada:

```text
adb -s <serial> shell monkey -p <pacote> -c android.intent.category.LAUNCHER 1
```

A primeira abertura descompacta os arquivos do app. Espere até existirem:

- `/storage/emulated/0/Android/data/<pacote>/files/retroarch.cfg`;
- a pasta `/storage/emulated/0/RetroArch/`.

Se depois de 3 minutos eles não existirem, tire uma captura de tela e procure o arquivo com `find /storage/emulated/0 -name retroarch.cfg`, porque a permissão de arquivos ou o caminho podem ser diferentes.

Guarde uma cópia do original no computador com o nome `retroarch.cfg.orig`. Esses caminhos valem para o Android 10 e podem mudar. Confirme em `libretro_directory`, `core_assets_directory` e `savefile_directory`, dentro do próprio arquivo.

## 5. Instalar o núcleo

Sem root, o ADB não grava na pasta privada do app. Existem dois caminhos, ambos pela tela:

**A. Por arquivo (testado):**

1. Extraia o `.so` do zip e confirme que combina com o aparelho. Nos bytes do ELF, o byte 4 vale 1 em 32 bits e 2 em 64 bits; o byte 18 vale 40 em ARM 32 e 183 em ARM 64.
2. Envie para a pasta de `core_assets_directory`, que no caso testado é `/storage/emulated/0/RetroArch/downloads/`.
3. No RetroArch: **Load Core → Install or Restore a Core → arquivo `.so`**.
4. Abra **Load Core** de novo e confirme que aparece "Sony - PlayStation (PCSX ReARMed)".
5. Apague o `.so` da pasta de downloads.

**B. Pela internet (não testado):** **Load Core → Download a Core**, com o aparelho no Wi-Fi.

Os menus são desenhados pelo próprio app, então `uiautomator` não ajuda. Tire uma captura de tela, leia a posição e toque com `input tap`. Faça isso a cada tela, porque as posições mudam com o aparelho e a orientação.

Dentro do jogo, os botões na tela responderam a toques de 150 ms: `input swipe <x> <y> <x> <y> 150`. Se não houver como tocar pelo ADB, passe as etapas para a pessoa fazer na tela.

## 6. BIOS

- **Sem BIOS:** o núcleo usa uma BIOS simulada. Funciona, mas a documentação avisa que a compatibilidade é menor.
- **Com a BIOS da pessoa:** coloque na pasta de `system_directory`, com nome como `scph5501.bin`, e confira o MD5 com a [documentação do núcleo](https://docs.libretro.com/library/pcsx_rearmed/). Não testado.

## 7. Configurar

O RetroArch regrava a configuração ao sair. **Feche com `am force-stop` antes de editar** e edite uma cópia:

```text
adb -s <serial> shell am force-stop <pacote>
adb -s <serial> pull <caminho>/retroarch.cfg retroarch.cfg
python -I scripts/retroarch-tools.py set retroarch.cfg screen_orientation=1 input_overlay_opacity=0.500000
adb -s <serial> push retroarch.cfg <caminho>/retroarch.cfg
```

| Chave | Valor | Motivo |
|---|---|---|
| `screen_orientation` | `1` | Tela sempre deitada, com a imagem bem maior |
| `input_overlay_opacity` | `0.500000` | Botões na tela atrapalham menos a imagem |
| `fps_show` | `true` só durante os testes | Mostra o contador de FPS |

O padrão do caso testado já vinha sem filtros (`video_shader_enable` e `video_smooth` falsos), com rebobinar e `run_ahead` desligados. Confira esses valores no aparelho e mantenha assim em hardware fraco.

Para abrir direto, útil nos testes:

```text
adb -s <serial> shell am start -n <pacote>/com.retroarch.browser.retroactivity.RetroActivityFuture -e ROM "<jogo>.cue" -e LIBRETRO /data/user/0/<pacote>/cores/pcsx_rearmed_libretro_android.so -e CONFIGFILE <caminho>/retroarch.cfg -e DATADIR /data/user/0/<pacote> -e SDCARD /storage/emulated/0 -e EXTERNAL /storage/emulated/0/Android/data/<pacote>/files
```

No Windows, escreva o comando inteiro entre aspas duplas depois de `adb shell` e os caminhos com espaços entre aspas simples.

**Controle físico (não testado):** a pessoa pareia o controle pelo Bluetooth do Android ou conecta por um adaptador OTG. O RetroArch reconhece muitos modelos sozinho; os demais são configurados em **Settings → Input → RetroPad Binds**, nomes que podem variar. Confirme com ela que os botões respondem. Depois, para esconder os botões na tela, use `input_overlay_enable=false`, com o app fechado. Se o Bluetooth tiver sido desligado em uma otimização, ligue-o de novo.

## 8. Deixar fácil de abrir

Crie a lista e envie para a pasta de listas:

```text
python -I scripts/retroarch-tools.py playlist "Sony - PlayStation.lpl" "<jogo no aparelho>.cue" /data/user/0/<pacote>/cores/pcsx_rearmed_libretro_android.so "Nome do Jogo"
adb -s <serial> push "Sony - PlayStation.lpl" /storage/emulated/0/RetroArch/playlists/
```

Com isso, o caminho é: ícone de lista → **Sony - PlayStation** → jogo → **Run**. Teste esse caminho no aparelho, pois é o que a pessoa vai usar.

## 9. Medir

O contador de FPS na tela serve como conferência rápida, mas não mostra engasgos. Meça com `scripts/frame-sample.sh`, rodando no aparelho, para resistir a quedas do USB:

```text
adb -s <serial> push scripts/frame-sample.sh /data/local/tmp/frame-sample.sh
adb -s <serial> shell "nohup sh /data/local/tmp/frame-sample.sh <pacote> 8 > /data/local/tmp/fs.out 2>&1 < /dev/null &"
adb -s <serial> shell tail -n 1 /data/local/tmp/fs.out
adb -s <serial> pull /data/local/tmp/fs.out fs.out
python -I scripts/frame-stats.py fs.out
adb -s <serial> shell rm /data/local/tmp/frame-sample.sh /data/local/tmp/fs.out
```

Repita o `tail` até aparecer `FIM`. Testado só no Android 10; em outras versões, o nome da camada pode mudar.

Para comparar de forma justa:

- **Meça uma cena 3D real**, porque vídeos e menus exigem bem menos. Depois de alguns segundos parado, muitos jogos abrem uma demonstração automática, o que serve como cena repetível.
- **Repita a mesma sequência**, com um novo início do jogo a cada vez, e meça a referência pelo menos duas vezes para conhecer a variação.
- **Não tire capturas de tela durante a medição.** No caso real, cada captura causou uma travada de cerca de 250 ms.
- **Com a tela bloqueada, não há o que medir:** o script avisa que não encontrou a camada.

Alvo: FPS perto da taxa do jogo e da tela, sem engasgos longos. O script mostra o período da tela em `periodo_tela_ms`: no caso testado, 16,67 ms, ou 60 Hz. Telas de 90 ou 120 Hz têm outro período. Jogos americanos e japoneses (NTSC) rodam a cerca de 60 FPS, e europeus (PAL), a 50 FPS.

## 10. Ajustar só se for preciso

Se a referência já estiver boa, não mexa. No caso real, separar vídeo e áudio em núcleos não trouxe ganho claro e foi removido, embora essa comparação tenha sido feita antes de descobrir que a captura de tela afetava a medição.

Se houver lentidão medida, teste uma opção por vez, sempre com a mesma cena. As opções ficam em `config/PCSX-ReARMed/PCSX-ReARMed.opt`, dentro da pasta do RetroArch, com o app fechado. Confirme pelo menu **Quick Menu → Core Options** que o valor foi aplicado, pois o caso real não fez essa confirmação.

| Opção | Valores | Efeito esperado | Situação |
|---|---|---|---|
| `pcsx_rearmed_gpu_thread_rendering` | `disabled`, `sync`, `async` | Vídeo em outro núcleo | `sync` sem ganho claro, em medição com captura de tela |
| `pcsx_rearmed_spu_thread` | `disabled`, `enabled` | Áudio em outro núcleo | Sem ganho claro, em medição com captura de tela |
| `pcsx_rearmed_frameskip_type` | `disabled`, `auto` | Pula quadros para manter a velocidade | Não testado |
| `audio_latency`, em `retroarch.cfg` | ms; padrão 128 no caso testado | Mais alto reduz chiado e aumenta o atraso do som | Não testado |

Não ative root nem overclock só para o jogo sem uma medição que mostre que a CPU é o limite, e sem passar pela etapa de root e kernel.

**Temperatura:** o caso real ficou entre 37 °C e 41 °C na bateria, carregando pelo USB. Se passar de cerca de 45 °C, pare e deixe esfriar.

## 11. O que a pessoa precisa testar

Pelo USB não dá para ouvir o som nem jogar de verdade. Peça que ela confira:

1. **Som:** se há chiados ou cortes.
2. **Controles:** se todos os botões respondem. O overlay do caso real tinha um segundo `L1` embaixo, não testado.
3. **Jogo controlado:** trechos reais podem pesar mais que a cena medida.
4. **Save:** salvar no jogo, fechar o RetroArch, abrir de novo e carregar. O cartão de memória fica em `saves/PCSX-ReARMed/` (`.srm`).
5. **Sair sem perder nada:** tocar no botão do RetroArch na tela, com o ícone do invasor, e usar **Quit RetroArch** no menu principal, em vez de só fechar o app. Assim, o cartão de memória e a configuração são gravados.

## 12. Relatório e como desfazer

No relatório, informe o emulador e a versão, a tabela medida, o que foi ajustado ou descartado, o caminho do jogo, o caminho dos saves, os testes que dependem da pessoa e se a BIOS é simulada.

Sem atualização automática fora de lojas, o RetroArch fica na versão instalada.

Para remover, depois de avisar que os saves ficam na pasta do RetroArch e copiá-los se a pessoa quiser:

```text
adb -s <serial> uninstall <pacote>
adb -s <serial> shell rm -rf /storage/emulated/0/RetroArch
adb -s <serial> shell rm -rf /storage/emulated/0/ROMs/PS1
```

Mostre a lista desses caminhos e peça confirmação antes de apagar, porque eles incluem os saves e o jogo.
