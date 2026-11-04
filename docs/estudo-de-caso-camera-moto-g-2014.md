# Estudo de caso: câmera do Moto G 2014

Registro do estudo e da melhoria da câmera no mesmo Moto G 2014 dos estudos de caso da [otimização](estudo-de-caso-moto-g-2014.md) e do [emulador](estudo-de-caso-ps1-moto-g-2014.md), feito pelo Claude Code com ADB em 3 de novembro de 2026.

Dados pessoais foram retirados. As fotos e os vídeos de teste foram apagados do aparelho e do computador. Nenhuma biblioteca proprietária faz parte deste repositório.

## Resumo

| Item | Resultado |
|---|---|
| Driver de câmera | Qualcomm HAL1 (mm-camera2), sem Camera2 nativo |
| App instalado | Open Camera 1.56.2, do F-Droid, configurado por arquivo |
| Vídeo 720p | De 9,9 para **20,0 Mbps** reais |
| HDR | O do app original travou; o do Open Camera funcionou em 23 s |
| Filtros | 8 efeitos ao vivo, 9 na galeria original e **16 na Fossify Gallery** |
| Foto noturna | Exposição forçada de 850 ms: **2,5 vezes mais clara e com menos ruído** |
| Câmera lenta | 60 fps real; 90 e 120 fps anunciados, mas falsos |
| CAC, ChromaFlash, OptiZoom e UbiFocus | Bibliotecas instaladas e testadas, sem efeito; removidas |
| Foto comum | Igual nos dois apps: o processamento é do chip |

## Aparelho e câmera

| Item | Valor |
|---|---|
| Sistema | LineageOS 17.1 não oficial (Android 10, compilação `userdebug`) |
| Processador | Snapdragon 400 (MSM8226), 32 bits |
| Câmera traseira | Sony IMX179, 8 MP (3264x2448), foco automático, flash |
| Câmera frontal | Sony IMX132, 2 MP (1920x1080), foco fixo |
| Sensores de movimento | Acelerômetro e giroscópio |
| App original | Snap, do LineageOS |

Os nomes dos sensores vieram de `/sys/class/video4linux/*/name`. A ROM traz arquivos de ajuste de outros sensores (OV8865, T4K71 e AR0543), usados em outros modelos da Motorola com o mesmo pacote.

## Varredura

`dumpsys media.camera` mostrou `device@1.0` e "API2 not directly supported" nas duas câmeras: o Camera2 é só uma camada de compatibilidade. Por isso:

- não há ISO, exposição nem balanço de branco manuais, nem RAW ou estabilização de vídeo;
- a GCam não é uma opção;
- o vídeo vai até 720p30, e o encoder aceita até 20 Mbps, enquanto o perfil gravava a 10 Mbps;
- o driver anuncia 8 efeitos de cor e 20 modos de cena.

## App e configuração

O Open Camera foi baixado de `f-droid.org/repo`, e o SHA-256 foi conferido com o `index-v2.json` oficial. A configuração foi feita por arquivo: o app exportou a própria configuração, o XML foi alterado no computador e o app restaurou. Itens alterados: JPEG a 100%, vídeo a 20 Mbps, grade de terços e botões de nivelamento e de detecção de rosto.

A opção "otimizar foco" não aparece com a API antiga, então não teve efeito.

## Medições de foto

Mesma cena com pouca luz (ISO 640, 1/16 s), celular apoiado:

| Teste | Tempo até salvar | Brilho | Ruído | Observação |
|---|---|---|---|---|
| Snap, padrão | 2,54 s (mediana de 3) | 120,5 | 1,63 | Referência |
| Open Camera, padrão | 3,76 s (mediana de 3) | 118,8 | 1,69 | Mesma imagem |
| Open Camera, DRO | 11,5 s | 124,4 | 2,11 | 38% mais detalhe |
| Open Camera, HDR | 23,4 s | 154,6 | 1,45 | 63% menos área estourada |
| Snap, HDR | não terminou | | | Travou o driver por mais de 90 s |

As fotos do Snap e do Open Camera no modo padrão tinham **a mesma tabela de quantização JPEG**. O driver ignora o pedido de qualidade do app, e só o DRO e o HDR, que o próprio app recomprime, saem a 100%.

As primeiras fotos do Open Camera saíram de lado. O acelerômetro marcava 9,78 m/s² no eixo Z: o celular estava deitado, com a câmera para baixo, e a orientação ficou indefinida. Os testes com o aparelho na mão não foram feitos.

## Vídeo e câmera lenta

| Teste | Resultado |
|---|---|
| Snap, 720p | 9,86 Mbps, 30 fps, AAC estéreo |
| Open Camera, 720p | **20,00 Mbps**, 30 fps, AAC estéreo |
| Câmera lenta 60 fps (Snap) | 2.261 quadros em cerca de 38,5 s reais: **~59 fps reais**, sem quadros repetidos |
| Câmera lenta 90 fps | 277 quadros em cerca de 9,9 s: **~28 fps**, marcado como 90 |
| Câmera lenta 120 fps | Recusada em 720p; em 480p, 306 quadros em cerca de 10 s: **~30 fps** |

A causa dos 90 e 120 falsos está no código aberto do adaptador de câmera do LineageOS para a família MSM8226 (`CameraWrapper.cpp`). Para este modelo, ele escreve à força a lista "60,90,120" e os tamanhos de câmera lenta, por cima do que o driver informa.

O vídeo de 60 fps em câmera lenta vira 720p a 59,97 fps em tempo real, sem perda, com `ffmpeg -itsscale 0.5 -i entrada.mp4 -c copy saida.mp4`.

## Engenharia reversa

As bibliotecas da câmera foram copiadas para o computador e lidas sem executar.

**Modos do sensor traseiro** (`libmmcamera_imx179.so`):

| Modo | Saída | Janela do sensor | fps máximo |
|---|---|---|---|
| 0 | 3264x2448 | sensor inteiro | 30 |
| 1 | 1640x924, binning 2x2 | faixa 16:9 da largura toda | 60 |

PLL de 648 MHz a partir de 24 MHz, com 259,2 milhões de pixels por segundo e 13,27 µs por linha. Não existe modo de 90 ou de 120 fps.

**Exposição automática** (arquivos chromatix): a foto, a prévia e o vídeo vão até 4.960 linhas (65,8 ms, ou 1/15 s), com ganho de até 16,2x. A câmera lenta vai até 1/61 s. Isso explica as fotos noturnas escuras: o modo automático não expõe por mais de 1/15 s.

**Propriedades lidas pelo driver**, com o valor padrão tirado do código: entre elas, `persist.camera.feature.cac=0`, `wavelet.enable=1`, `morphonr.enable=1`, `post_altm.enable=0`, `gtmmode.enable=0`, `mtnrstill.enable=0` e `is_type=0`. O módulo de sensor da Motorola lê também `mot_exp=33.3`, `mot_gain=1.0`, `use_realexp=1` e `motexp_update=0`.

As ferramentas usadas viraram `scripts/camera-libs-scan.py` e `scripts/qcom-camera-tuning.py`.

## Recursos ocultos testados

As propriedades `persist.camera.*` tinham o rótulo genérico `default_prop`, e o shell do ADB conseguia gravá-las sem root.

| Propriedade | Resultado |
|---|---|
| `mot_exp`, `mot_gain`, `motexp_update` | **Funciona.** O driver registrou `LINECOUNT 64046` (850 ms). Brilho de 21,7 para 58,1, ruído de 0,85 para 0,74, e as sombras sem detalhe caíram de 10,8% para 0,6% |
| `post_altm.enable` | Sem efeito: imagem igual à base, dentro da variação entre duas fotos |
| `gtmmode.enable` | O driver registrou "GTM mode enabled", mas a imagem ficou igual |
| `mtnrstill.enable` | Sem efeito |

O limite da exposição forçada é cerca de 0,85 s, porque o registrador de exposição do sensor tem 16 bits. O EXIF da foto continua mostrando os valores automáticos.

## Bibliotecas de recursos

A pedido da pessoa, foram procuradas as bibliotecas que o código cita e que não existiam: `libmmcamera_cac2_lib`, `libmmcamera_chromaflash_lib`, `libmmcamera_optizoom_lib` e `libmmcamera_ubifocus_lib`, com seus algoritmos. A redução de ruído da Morpho já vinha embutida em `libmmcamera_imglib.so`.

1. O conjunto foi baixado dos arquivos de fábrica do Yu Yutopia, no repositório TheMuppets que o LineageOS usa, e conferido pelo hash do Git.
2. A compatibilidade estática passou: ARM 32 bits, dependências presentes e as mesmas funções procuradas (`img_algo_*` e `cac2_*`).
3. A primeira tentativa de copiar para o sistema foi **bloqueada pelo Claude Code**, por ser código baixado de fora. Foi feita depois que a pessoa autorizou explicitamente.
4. Com root pelo ADB, os 7 arquivos foram só acrescentados em `/system/vendor/lib`. O serviço de câmera registrou "loaded successfully" para os três módulos.
5. Nenhuma opção nova apareceu. A análise do driver da Motorola (`camera.vendor.msm8226.so`) mostrou **zero referências no código** a `opti-zoom`, `chroma-flash` e `af-bracket`: as funções que ligam esses recursos nunca são chamadas. O CAC entra na máscara de reprocessamento, mas o pós-processamento da Motorola nunca chama o módulo.
6. Os arquivos foram removidos, a câmera foi testada nos dois apps e o root foi desligado.

## Incidentes

- **Conexão USB:** caiu muitas vezes. Os testes passaram a rodar no próprio aparelho com `nohup`, e os comandos curtos, a repetir sozinhos.
- **Snap:** ficou em modo vídeo depois de uma visita ao menu e precisou ser devolvido ao modo foto.
- **Open Camera:** a explicação do HDR na primeira vez recebeu o toque do disparo, e a lista de restauração tinha uma linha "Parent Folder" que deslocou a posição dos arquivos.
- **Root pelo ADB:** a opção não desligava pelo toque e só desligou com foco por teclado. Numa checagem, rodar `adb root` com a opção ainda ligada devolveu o root ao ADB. Isso foi desfeito em seguida.
- **Segurança:** o SELinux desta ROM não oficial está em modo permissivo. Não foi alterado, mas reduz a proteção do sistema.

## Não verificado

- Fotos com luz do dia e com o celular na mão.
- Câmera frontal.
- Panorama, que exige mover o aparelho.
- Diferença visível do vídeo a 20 Mbps (só a taxa foi medida).
- A exposição longa com a câmera frontal, que está na lista do código.
- Qualquer outro aparelho.

## Como desfazer

- **Apps:** desinstale o Open Camera (`net.sourceforge.opencamera`) e a Fossify Gallery (`org.fossify.gallery`).
- **Configuração:** a original do Open Camera ficou salva no próprio app (Settings manager → Restore settings).
- **Propriedades:** as que foram usadas ficaram vazias, e o driver volta aos valores padrão.
- **Sistema:** nenhum arquivo permaneceu alterado.
