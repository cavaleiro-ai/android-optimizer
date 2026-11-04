# Câmera

Varre o hardware e o software da câmera, mede o ponto de partida e aplica só as melhorias que a medição confirmar: app de câmera, vídeo, filtros, recursos ocultos do driver e, no último nível, arquivos do sistema.

**Até onde isto foi testado:** um único aparelho, o Moto G 2014 (Snapdragon 400, 32 bits, câmera Qualcomm HAL1, LineageOS 17.1). Aparelhos com Camera2 completo, 64 bits, outros fabricantes e drivers Qualcomm CamX não foram testados: siga a varredura e pesquise o modelo exato. O registro completo, inclusive das falhas, está em `docs/estudo-de-caso-camera-moto-g-2014.md` no repositório da skill.

**Comandos:** os scripts `.sh` rodam no aparelho (`adb push` para `/data/local/tmp` e `adb shell sh ...`); os `.py` rodam no computador, com Python 3. No Git Bash, use `MSYS_NO_PATHCONV=1` antes de comandos com caminhos do aparelho.

Etapas: [limites](#limites) · [perguntas](#perguntas) · [1 varredura](#1-varredura) · [2 medir](#2-medir-o-ponto-de-partida) · [3 app](#3-app-de-câmera) · [4 filtros](#4-filtros) · [5 vídeo](#5-vídeo-e-câmera-lenta) · [6 recursos ocultos](#6-recursos-ocultos-do-driver) · [7 sistema](#7-análise-profunda-e-arquivos-do-sistema) · [8 limpeza](#8-limpeza-e-relatório)

## Limites

- **Não prometa qualidade que o sensor não entrega.** No modo normal, quem processa a foto é o chip de imagem do aparelho: dois apps costumam gerar a mesma imagem. Os ganhos reais vêm de modos de captura (HDR, DRO, exposição longa), de mais bitrate no vídeo e de recursos que o app original esconde.
- **Apps só de fonte oficial e com hash conferido**: F-Droid, site do desenvolvedor ou loja oficial. A GCam modificada vem de terceiros: explique o risco e só instale se a pessoa pedir, depois de confirmar que o aparelho tem Camera2 FULL ou LEVEL_3.
- **Bibliotecas de câmera de outros aparelhos** (os "blobs" da Qualcomm ou do fabricante) só entram no nível D, com confirmação específica, depois de provar na etapa 7 que o driver usa o recurso. Nunca sobrescreva um arquivo do sistema e nunca publique essas bibliotecas: elas têm licença do fabricante. Se o Claude Code bloquear a cópia de código baixado para o sistema, não contorne: explique e deixe a pessoa decidir.
- **Fotos de teste mostram o ambiente da pessoa.** Avise antes de fotografar, mantenha as cópias só na pasta temporária, não envie a serviços externos e apague tudo no fim.
- **Mantenha o app original.** Ele pode ter recursos que o novo não tem, como câmera lenta e leitor de QR. Pergunte antes de mudar o app padrão.

## Perguntas

Junte estas às que faltarem da entrevista, em uma mensagem só:

1. O que mais incomoda: fotos com pouca luz, fotos de dia, vídeo, câmera lenta, falta de filtros ou demora para tirar a foto?
2. Aceita instalar um app de câmera e uma galeria de código aberto? O app original continua como padrão?
3. Até onde ir na câmera?
   - **Só apps e ajustes**, sem root (recomendado).
   - **Recursos ocultos do driver**, ligados pelo ADB e sempre desfeitos no fim.
   - **Arquivos do sistema**, com root: pode deixar a câmera sem abrir até desfazer.
4. Durante os testes, o celular pode ficar apoiado, apontado para uma cena com luz?

## 1. Varredura

Só leitura. Rode no aparelho e guarde o resultado no computador:

```text
adb -s <serial> push scripts/camera-scan.sh /data/local/tmp/
adb -s <serial> shell sh /data/local/tmp/camera-scan.sh > camera-scan.txt
```

Se o app da câmera nunca foi aberto desde o boot, abra uma vez antes: em HAL1, os parâmetros só aparecem depois disso. Leia o relatório assim:

| No relatório | Significa | O que dá para fazer |
|---|---|---|
| `device@1.0` e `API2 not directly supported` | HAL1: o Camera2 é só uma camada de compatibilidade | Open Camera com a API antiga. Sem GCam, sem RAW, e ISO manual só se houver `iso-values` |
| `supportedHardwareLevel` LEGACY ou LIMITED | Camera2 parcial | Open Camera em parte dos recursos. GCam quase nunca funciona |
| FULL ou LEVEL_3, com `RAW` e `MANUAL_SENSOR` | Camera2 completo | Open Camera com Camera2 (RAW, ISO, exposição e redução de ruído). GCam possível, de fonte de terceiros |
| `video-hfr-values` ou `hfr-size-values` | Câmera lenta anunciada | Confirme o fps real na etapa 5, porque a lista pode ser falsa |
| `encoder ... max` acima do bitrate do perfil | Há margem para mais bitrate | Suba o bitrate no app até esse máximo |
| Giroscópio | Panorama | Modo PANO do Open Camera |
| `libmmcamera*` e `libchromatix*` | Qualcomm mm-camera2, de 2013 a 2016 | As ferramentas das etapas 6 e 7 se aplicam |
| `camx`, `com.qti.sensormodule` | Qualcomm CamX, de 2017 em diante | As ferramentas das etapas 6 e 7 não foram feitas para ele |

Com o nome do sensor (`SENSOR_MODELS`), pesquise a ficha técnica e o que outros donos do modelo relatam. Abra também o app original e leia o menu com `uiautomator dump`: modos, filtros, HDR e câmera lenta que ele já oferece.

## 2. Medir o ponto de partida

Use a mesma cena para todos os apps e modos, com luz, e o celular apoiado. **Não deixe o celular deitado:** com a câmera apontada para baixo, a orientação fica indefinida e as fotos saem de lado.

- **Tempo do toque até a foto salva:** `scripts/camshot.sh <rótulo> <pasta> <x> <y>`, rodando no aparelho com `nohup`. Pegue as coordenadas do botão com `uiautomator dump`. Use a mediana de 3 fotos.
- **Imagem:** `python -I scripts/imgstats.py <fotos...> --crops recortes.png` dá qualidade JPEG estimada, exposição, ISO, brilho, áreas estouradas, nitidez, ruído e um recorte central para olhar. A nitidez só se compara com o mesmo enquadramento.
- **Qualidade JPEG real:** se duas fotos saem com o mesmo `q`, o driver ignorou o pedido do app. No caso real, 100% virou o mesmo valor fixo do app original.
- **Vídeo:** grave 10 a 15 s e rode `python -I scripts/mp4info.py <vídeo>`, que mostra a taxa real de vídeo e áudio e o fps.

Mantenha a tela ligada durante os testes (`settings put global stay_on_while_plugged_in 2`), anote o valor original e restaure no fim.

## 3. App de câmera

**Open Camera** (F-Droid, GPL): funciona com HAL1 e com Camera2, e tem HDR e DRO por software, panorama com giroscópio, bracketing de exposição, grade, nivelamento, timer, disparo repetido, botão de volume como disparador e bitrate de vídeo ajustável.

1. Baixe o APK de `https://f-droid.org/repo/` e confira: `python -I scripts/fdroid-verify.py net.sourceforge.opencamera <apk>`. Instale só com `CONFERE` e com o Android mínimo e as ABIs compatíveis.
2. Dê `CAMERA` e `RECORD_AUDIO` com `pm grant`. Localização só se a pessoa quiser o GPS nas fotos.
3. Configure por arquivo, o que é exato e reproduzível:
   - no app, Configurações → Settings manager → Save settings;
   - traga o XML de `/sdcard/Android/data/net.sourceforge.opencamera/files/backups/`;
   - gere o novo com `python -I scripts/opencamera-config.py salvo.xml novo.xml --preset qualidade preference_video_bitrate=<máximo do encoder>`;
   - envie para a mesma pasta e use Restore settings. A lista começa com uma linha "Parent Folder": leia as posições na tela antes de tocar;
   - confira o resultado na tela de configurações, por exemplo Image quality = 100%.
4. Teste cada modo na mesma cena. Na primeira vez em HDR e PANO aparece uma explicação: toque em OK, ou o disparo seguinte cai nela.

No caso real (pouca luz, ISO 640):

| Modo | Tempo até salvar | Resultado medido |
|---|---|---|
| Padrão | 3,8 s (app original: 2,5 s) | Igual ao app original |
| DRO | 11,5 s | 38% mais detalhe e 25% mais ruído |
| HDR | 23 s | 63% menos área estourada e 14% menos ruído, um pouco mais macia |

**Teste os modos do app original antes de recomendá-los.** No caso real, o HDR por hardware do app Snap travou a câmera por mais de 90 s sem gerar foto. Ele foi deixado desligado, e o HDR do Open Camera ficou como alternativa.

## 4. Filtros

- **Ao vivo:** os efeitos de cor do driver (`effect-values`, por exemplo mono, sépia, negativo, solarizar, posterizar e aqua) e os modos de cena. No Open Camera, ficam no menu ⋮ → Color effect e Scene mode. O app original costuma ter um botão de filtros com os mesmos efeitos.
- **Depois da foto:** o editor da galeria do sistema (a Gallery do AOSP tem 9 filtros) ou o **Fossify Gallery** (F-Droid, GPL), com 16 filtros: Struck, Clarendon, OldMan, Mars, Rise, April, Amazon, Starlit, Whisper, Lime, Haan, BlueMess, Adele, Cruz, Metropolis e Audrey. Confira com `fdroid-verify.py`. Ele registra uma tarefa leve que roda quando surge foto nova.
- Não instale apps de filtros de fontes desconhecidas nem cheios de anúncios.

## 5. Vídeo e câmera lenta

- **Bitrate:** suba até o `maxBitRate` do encoder mostrado na varredura e confira com `mp4info.py`. No caso real, foi de 9,9 para 20,0 Mbps em 720p30, com arquivos 2 vezes maiores.
- **Câmera lenta: confirme o fps de verdade.** Grave e conte os quadros contra o tempo real: o nome do arquivo marca o início, e a data de modificação (`stat -c %y`) marca o fim. O metadado `com.android.capture.fps` só repete o que foi pedido. Confira também se há quadros repetidos, por exemplo com o `ffmpeg` extraindo quadros. No caso real, 60 fps era real, mas 90 e 120 fps capturavam uns 30 fps: o adaptador de câmera do LineageOS anunciava modos que o sensor não tem.
- **Câmera lenta em vídeo fluido:** um vídeo de 60 fps gravado como câmera lenta vira 60 fps em tempo real no computador, sem perda: `ffmpeg -itsscale 0.5 -i lento.mp4 -c copy 60fps.mp4`. O resultado continua sem som.

## 6. Recursos ocultos do driver

Nível "recursos ocultos". Tudo aqui se desfaz limpando as propriedades.

1. Copie para uma pasta vazia do computador o driver e as bibliotecas da lista `CAMERA_LIBRARIES` da varredura, com `adb pull`.
2. Rode `python -I scripts/camera-libs-scan.py props <pasta>` para ver as propriedades que o código lê. Com `capstone` e `pyelftools` instalados num ambiente virtual (`python -m venv`), ele mostra também os valores padrão. Isso só funciona com bibliotecas ARM de 32 bits.
3. Veja se o shell pode gravar: `setprop <prop> <valor padrão>`. Se der erro, só com root.
4. Teste uma propriedade por vez: grave, reabra a câmera, fotografe a mesma cena, compare com `imgstats.py` e limpe com `setprop <prop> ''`. Propriedades lidas na abertura da câmera exigem fechar o app, e algumas só valem depois de reiniciar o processo do driver (etapa 7).
5. No fim, limpe todas as que você gravou.

**Exposição longa nos aparelhos Motorola com mm-camera2.** O módulo de sensor tem um recurso de teste: `persist.camera.mot_exp` (em ms), `mot_gain`, `use_realexp=1` e `motexp_update=1`. Ele vale para os sensores listados no próprio código, conferidos com `camera-libs-scan.py refs`. No caso real, o shell podia gravá-las sem root. Com 850 ms e ganho 4x, a foto noturna ficou 2,5 vezes mais clara, com menos ruído e com detalhe nas sombras. O limite foi cerca de 0,85 s (65.535 linhas do sensor). `scripts/long-exposure.sh <ms> <ganho>` faz tudo e sempre desliga no fim, com o Open Camera aberto e o celular apoiado. Os dados EXIF continuam mostrando os valores automáticos.

Também foram testadas `post_altm`, `gtmmode` e `mtnrstill`, e as fotos saíram idênticas. Não dê nenhuma como melhoria sem comparar as fotos.

## 7. Análise profunda e arquivos do sistema

Só nos níveis D ou E, com a confirmação específica do passo 4 do fluxo principal.

**Entender os limites do sensor** (mm-camera2, 32 bits):

```text
python -I scripts/qcom-camera-tuning.py modes libmmcamera_<sensor>.so
python -I scripts/qcom-camera-tuning.py aec libchromatix_<sensor>_snapshot.so
```

`modes` mostra os modos reais do sensor (resolução, binning e fps máximo). `aec` mostra a exposição mais longa e o ganho máximo do modo automático, o que explica fotos noturnas escuras. No caso real, o sensor tinha só 3264x2448 a 30 fps e 1640x924 a 60 fps, e a exposição automática parava em 1/15 s. Um modo de 90 fps exigiria editar o binário do sensor (fps = taxa de pixels / (comprimento da linha × linhas por quadro)). Não faça isso como tentativa de melhoria: o risco é alto e não foi testado.

**Instalar bibliotecas que faltam** (CAC, ChromaFlash, OptiZoom, UbiFocus e semelhantes). Só siga se todos os itens forem verdadeiros:

1. `camera-libs-scan.py missing <pasta>` aponta a biblioteca como citada e ausente.
2. `camera-libs-scan.py refs <driver.so> <chave>` acha referências no código para a chave que liga o recurso (`opti-zoom`, `chroma-flash`, `af-bracket` e assim por diante). **Se der 0, pare:** o driver nunca vai ligar o recurso. No caso real, deu 0 para os três, e as bibliotecas instaladas não mudaram nada.
3. A biblioteca candidata é da mesma geração de chip e de Android, exporta as funções que o módulo procura (veja os textos perto do nome da biblioteca no módulo) e tem todas as dependências no aparelho.
4. A instalação só acrescenta arquivos. Anote a lista: para desfazer, basta apagar.

Passos técnicos que funcionaram no LineageOS 17.1:

- **Root pelo ADB:** ligue Opções do desenvolvedor → Rooted debugging, depois `adb root` e `adb remount`. O aviso `remount failed` pode vir só das partições APEX: confira com `touch` na pasta de destino.
- **Rótulo dos arquivos:** copie o dos vizinhos (`ls -lZ`), por exemplo `chown root:root`, `chmod 644` e `chcon u:object_r:vendor_file:s0`.
- **Recarregar a câmera:** reinicie o serviço da câmera e também o processo que carrega o driver. Descubra qual é com `grep -l <driver.so> /proc/*/maps`; no caso real era o `mediaserver`. Sem isso, a lista de recursos antiga continua em memória.
- **Prova:** o log mostrar "loaded successfully" não basta. A nova chave precisa aparecer nos parâmetros que o app recebe, e uma foto precisa mudar. Se nada mudar, remova os arquivos.
- **Desligar o root no fim:** use `adb unroot` e `mount -o remount,ro /`, e desligue Rooted debugging. Na 17.1, o toque não desligava a opção, mas funcionou levar o foco até ela com `input keyevent 20` e confirmar com `input keyevent 23`. Confira com `service call adbroot_service 2`, que deve devolver 0.

## 8. Limpeza e relatório

- **Fotos e vídeos de teste:** liste-os com `content query --uri content://media/external/file --projection _id:_data --where "_data LIKE '%/DCIM/%'"`, confira as datas e apague pelo `_id` com `content delete`, além de `rm`.
- **Arquivos temporários:** remova os scripts de `/data/local/tmp`, limpe as propriedades gravadas e restaure o tempo de tela.
- **App original:** se você abriu o modo vídeo dele, devolva ao modo foto.
- **Relatório:** traga a tabela medida, o que mudou e como desfazer (desinstalar apps, Restore settings com o arquivo original do Open Camera, propriedades vazias). Diga também o que não foi testado, por exemplo luz do dia com o celular na mão, câmera frontal e panorama.
