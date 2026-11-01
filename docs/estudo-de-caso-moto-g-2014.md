# Estudo de caso: Moto G 2014 (XT1069)

Registro de tudo o que foi feito no projeto que deu origem à skill: um celular de 2014, conectado por USB a um PC com Windows 10, operado pelo Claude Code com ADB e Fastboot, em 31 de outubro e 1º de novembro de 2026.

Dados pessoais foram retirados: número de série, conta, rede Wi-Fi, senha e códigos de desbloqueio.

## Resumo

| Item | Resultado |
|---|---|
| Sistema | Android 6.0 → **LineageOS 17.1 (Android 10)** |
| Abertura do WhatsApp | 3,46 s → **2,05 s** (41% menos) |
| Abertura do Telegram | 4,64 s → **3,36 s** (28% menos) |
| Recuperação de fotos apagadas | **Nada recuperado** |
| Root e overclock | **Não feitos.** Só levantamento das opções |

## Aparelho

| Item | Valor |
|---|---|
| Modelo | Motorola Moto G 2ª geração, XT1069 (dois chips, TV digital, Brasil) |
| Codinome | `titan` (`titan_udstv` no sistema de fábrica) |
| Chip | Qualcomm MSM8226 (Snapdragon 400), 4 núcleos até 1,19 GHz |
| GPU | Adreno 305: 200, 320 e 450 MHz |
| RAM | 1 GB (906 MB utilizáveis) |
| Armazenamento | 16 GB |
| Sistema inicial | Android 6.0, patch de agosto de 2016, bootloader `0x4887` |
| Kernel final | 3.4.113 |

## Ferramentas

| Ferramenta | Versão | Origem |
|---|---|---|
| Android Platform-Tools | 37.0.1 | `winget`, Google |
| Motorola Mobile Drivers | 6.4.0 | `winget`, Motorola |
| TWRP | 3.3.1-0-titan | [dl.twrp.me/titan](https://dl.twrp.me/titan/), com checksum confirmado |
| LineageOS | 17.1, build de 13/08/2020, não oficial | [Blog Projeto Moto G](http://projetomotog.blogspot.com/2020/06/rom-lineageos-171-android-10-unofficial.html) |
| WhatsApp | 2.26.43.72 | [whatsapp.com/android](https://www.whatsapp.com/android/) |
| Telegram | 13.1.0 | [telegram.org](https://telegram.org/dl/android/apk) |

A ROM não tem checksum publicado. A integridade foi conferida apenas pela chave do link de download. Esta skill não distribui nenhum desses arquivos.

## Linha do tempo

### 1. Tentativa inicial com um iPhone

O projeto começou com um iPhone, mas o Windows não o detectou e o trabalho seguiu para o Moto. Nada foi feito no iPhone. Esta skill é só para Android.

### 2. Identificação

O Windows mostrava também um tablet Samsung, e a pessoa avisou que ele não era o alvo. A partir daí, todos os comandos usaram o serial do Moto.

### 3. Escolha da ROM

Não foi encontrada nenhuma build acima do Android 10 para o `titan`, embora o fórum XDA não tenha sido acessível às ferramentas automáticas. Foi escolhida a build do blog brasileiro por ser declarada como testada no XT1069.

A pessoa pediu "a última versão". Foi explicado que o Android mais recente não existia para esse aparelho.

### 4. Verificações antes de instalar

- A ROM aceitava o codinome `titan_udstv` e os bootloaders `0x4882|0x4883|0x4886|0x4887`.
- O aparelho tinha o bootloader `0x4887`.
- Bateria em 100%.

### 5. Recuperação de fotos

No meio do processo, a pessoa pediu para recuperar fotos e vídeos apagados.

- **Antes do desbloqueio:** só havia 11 arquivos legíveis, nenhum de mídia. O cache da galeria estava vazio (arquivos de 4 bytes).
- **Conta no aparelho:** havia uma conta Google diferente da usada na sessão. Perguntou-se de quem era; a pessoa disse que era dela.
- **Depois do desbloqueio:** a partição de dados (12,9 GB) foi copiada e conferida por checksum, mas **estava 100% zerada**.

O desbloqueio apagou tudo antes que fosse possível ler a memória, então nada foi recuperado. A cópia foi excluída.

### 6. Desbloqueio

1. A primeira leitura falhou porque faltava o driver de Fastboot; foi instalado.
2. `fastboot oem get_unlock_data` gerou o texto para o site da Motorola.
3. A pessoa entrou no site com a própria conta e recebeu o código por e-mail. Esta etapa precisou ser manual.
4. `fastboot oem unlock <código>` confirmou `unlocked: yes`. A garantia ficou anulada (`iswarrantyvoid: yes`).

Confusões a evitar: a pessoa entendeu "bloqueado" como tela travada e achou que precisava do e-mail antigo do aparelho.

### 7. Instalação

1. `fastboot boot twrp.img` abriu o TWRP sem gravar nada.
2. `fastboot flash recovery twrp.img` gravou o TWRP.
3. `twrp format data` não existia nessa versão. `twrp wipe data` não conseguiu montar a partição zerada, formatou o cache, apagou a ROM enviada e travou o TWRP.
4. O TWRP foi reiniciado, a partição `userdata` (confirmada pelo nome) foi formatada com `make_ext4fs` e montada com sucesso.
5. A ROM foi reenviada e conferida por checksum. `twrp install` terminou com `script succeeded`.
6. A primeira inicialização parecia ter falhado, porque o ADB não voltou em 15 minutos. Na verdade, ele vem desligado: o Windows já mostrava o aparelho em transferência de arquivos. A pessoa ativou a depuração USB e tudo foi confirmado: Android 10, `boot_completed=1`.

### 8. Rede e apps

- O Wi-Fi foi conectado pela tela, com `input`, porque o Android 10 não permite comandos de Wi-Fi para o usuário do ADB. A senha entrou com 2 caracteres a mais por causa das aspas; o campo foi conferido sem exibir o conteúdo e corrigido antes de conectar. O teste de ping chegou sem perdas.
- WhatsApp e Telegram foram instalados com `adb install`. Abriram sem travar. O registro das contas não foi testado.

### 9. Limpeza de apps

Foram desativados 24 apps em duas levas, além de 1 que já vinha desativado. Nenhum foi excluído.

- **Primeira leva:** impressão (3), protetores de tela (2), seletor de papel de parede animado, Easter egg, Traceur, Dynamic System, Hotspot 2.0, ANT+ e provedor de favoritos.
- **Segunda leva:** backups locais (4), `managedprovisioning`, Bluetooth MIDI, `htmlviewer`, perfis do Lineage, AudioFX e apps de papel de parede (3).

Na segunda leva, o primeiro reinício veio cedo demais e as desativações se perderam. O problema foi detectado pela contagem: 13 em vez de 25. Foi repetido com uma espera de 45 segundos.

O ganho medido foi pequeno: cerca de 20 MB de RAM livre (378 → 398 MB), em uma única medição. O AudioFX continuou rodando depois de desativado.

### 10. Otimização e medição

Aplicado:

- animações em 0;
- buscas de Wi-Fi e Bluetooth em segundo plano desligadas;
- Bluetooth, tela ambiente, vibração e sons de toque desligados;
- limite de 12 apps em cache;
- apps do sistema compilados em `speed`, WhatsApp e Telegram em `speed-profile`.

Mediana de 3 aberturas, em milissegundos:

| App | Antes | Depois | `low_ram` (descartado) |
|---|---|---|---|
| Configurações | 502 | 440 | 442 |
| Calculadora | 631 | 509 | 504 |
| Telefone | 787 | 729 | 694 |
| Mensagens | 609 | 534 | 547 |
| WhatsApp | 3.463 | 2.046 | 2.809 |
| Telegram | 4.642 | 3.358 | 3.626 |

RAM livre ao fim de cada teste: 232 MB antes, 300 MB depois e 296 MB com `low_ram`.

**Limites da medição:**

- Foram 3 aberturas por app.
- O tempo desde o último reinício era diferente: ao fim de cada teste, 19 min antes, 12 min depois e 9 min com `low_ram`.
- Não foi isolado o efeito de cada ajuste.
- A primeira abertura após reiniciar pode ser bem mais lenta: as Configurações levaram 1,2 s.
- Só o tempo de abertura foi medido, não a fluidez.
- Não foi verificado se o limite de 12 apps em cache teve efeito real. Só se confirmou que o valor ficou gravado.

**Testados e descartados:**

- `speed` no WhatsApp: em 10 minutos, usou só 3 minutos de CPU e 465 MB de RAM. Foi interrompido após quase 30 minutos, reiniciando o aparelho.
- `ro.config.low_ram=true`: piorou o WhatsApp em 37%, sem ganho de RAM. O `build.prop` foi restaurado e o checksum original foi confirmado.

### 11. Opções de overclock

Só foram levantadas. A pessoa pediu para informar as opções, e a execução ficou pendente.

| Opção | Situação encontrada |
|---|---|
| Modo desempenho, nas frequências oficiais | Possível com root |
| Overclock de CPU | Exige kernel próprio. Nenhum kernel testado foi encontrado para Android 10 no `titan` |
| Overclock de GPU | Nenhum valor testado encontrado |
| Overclock de RAM | Nada confiável encontrado; não recomendado |

## O que não foi verificado

- Ligações, dados móveis e os dois chips (sem chip inserido).
- Foto e som na prática: o sistema reconheceu as duas câmeras e o áudio, mas sem teste real.
- TV digital, GPS e sensores.
- Uso prolongado: estabilidade, bateria e notificações.
- Registro e uso do WhatsApp e do Telegram.
- Qualquer outro aparelho. **A skill só foi executada de verdade neste Moto G.**

## Estado final do aparelho

| Item | Estado |
|---|---|
| Sistema | LineageOS 17.1, patch de 05/08/2020, sem atualizações |
| Bootloader | Desbloqueado |
| Recovery | TWRP 3.3.1-0 |
| Apps do Google | Não instalados |
| Apps | WhatsApp e Telegram |
| Emulador | RetroArch, instalado depois: veja o [estudo de caso do PS1](estudo-de-caso-ps1-moto-g-2014.md) |
| Root | Não instalado |
| Depuração USB | Ligada |

## Como desfazer

Como exemplo, os ajustes deste caso são revertidos com:

```text
settings put global window_animation_scale 1
settings put global transition_animation_scale 1
settings put global animator_duration_scale 1
settings delete global activity_manager_constants
settings put global bluetooth_on 1
settings put system haptic_feedback_enabled 1
settings put system sound_effects_enabled 1
pm enable <pacote>
cmd package compile --reset <pacote>
```

Voltar ao sistema de fábrica exigiria o firmware oficial do modelo. Isso não foi feito nem testado neste projeto.

## Lições

Estão em [`skills/android-optimizer/references/lessons.md`](../skills/android-optimizer/references/lessons.md). As duas mais importantes:

1. **Faça o backup antes do desbloqueio.** Depois, pode não restar nada.
2. **Meça tudo e desfaça o que não ajudar.** Uma dica popular piorou o resultado.

## Fontes

- [LineageOS: Moto G 2014 (titan)](https://wiki.lineageos.org/devices/titan/)
- [Guia de instalação para o titan](https://wiki.lineageos.org/devices/titan/install/)
- [TWRP para o Moto G 2014](https://twrp.me/motorola/motorolamotog2014.html)
- [Tópico da ROM no XDA](https://xdaforums.com/t/rom-unofficial-10-0-lineageos-17-0-titan.3997639/)
- [Blog Projeto Moto G](http://projetomotog.blogspot.com/2020/06/rom-lineageos-171-android-10-unofficial.html)
- [Flash com Fastboot (AOSP)](https://source.android.com/docs/setup/test/running)
- [Registro de 1.593 MHz no MSM8226 (HWBOT)](https://hwbot.org/submission/3043672_?lang=en)
