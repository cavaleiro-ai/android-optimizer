# Ajustes reversíveis (sem root)

Antes de mudar, leia cada valor com `settings get` e grave no `android-optimizer-log.md`. `null` significa que o valor não existia; para restaurar, use `settings delete`.

## Fluidez

```text
settings put global window_animation_scale 0
settings put global transition_animation_scale 0
settings put global animator_duration_scale 0
```

Efeito: as telas trocam sem transição. É o ganho mais perceptível no uso, embora não melhore o tempo real de processamento. Se a pessoa estranhar, use `0.5`.

## Abertura de apps

Compilação ART (Android 7 ou mais novo):

```text
cmd package compile -m speed -f <pacote>           # apps pequenos e do sistema
cmd package compile -m speed-profile -f <pacote>   # apps grandes, já abertos antes
cmd package compile --reset <pacote>               # desfaz
```

- **Apps grandes:** não use `speed`. No caso real, compilar um APK de 148 MB em um aparelho com 1 GB consumiu mais de 460 MB de RAM e travou por quase 30 minutos. `speed-profile`, depois de abrir o app algumas vezes para gerar o perfil, terminou em 2 minutos e reduziu a abertura em 41%, junto com os demais ajustes.
- **Temperatura:** acompanhe com `dumpsys battery`, em décimos de grau. Pare de compilar perto de 45 °C.
- **Duração:** o ganho pode cair quando o app é atualizado. Recompile depois.

Também é útil: `cmd package bg-dexopt-job` otimiza o que estiver pendente, e `sm fstrim` faz a limpeza do armazenamento (pode não existir em alguns aparelhos).

## Menos trabalho em segundo plano

```text
settings put global wifi_scan_always_enabled 0
settings put global ble_scan_always_enabled 0
settings put global bluetooth_on 0                 # vale ao reiniciar
settings put secure doze_enabled 0                 # tela ambiente, quando existir
settings put secure doze_always_on 0
settings put system haptic_feedback_enabled 0
settings put system sound_effects_enabled 0
```

Efeitos: buscas de localização menos precisas, Bluetooth desligado (a pessoa religa no painel rápido) e sem vibração e som ao tocar.

## Limitar apps em cache (com cuidado)

Pergunte antes, porque os apps em segundo plano fecham mais cedo e as notificações podem atrasar:

```text
settings put global activity_manager_constants max_cached_processes=12
device_config put activity_manager max_cached_processes 12   # Android 10 ou mais novo
```

Para desfazer: `settings delete global activity_manager_constants` e `device_config delete activity_manager max_cached_processes`.

O suporte muda por versão. Gravar o valor não prova efeito: confira com `dumpsys activity settings` e teste com a medição.

## Limites do que não exige root

Sem root ou sem acesso ao sistema, não dá para mudar kernel, governor, swappiness, ZRAM nem `build.prop`.

Apps de "limpar RAM" e fechar apps à força normalmente pioram, porque o Android precisa reabrir tudo do zero.

## Editar `build.prop` (só com recovery personalizado)

Requer acesso à partição do sistema, então pertence às etapas de bootloader e recovery. Se for testar, grave uma cópia antes, confira o checksum, altere uma coisa por vez, meça e desfaça se não melhorar. `ro.config.low_ram=true` não é um ganho garantido: no caso real, abrir o WhatsApp ficou 37% mais lento.
