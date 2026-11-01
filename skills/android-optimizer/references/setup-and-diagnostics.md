# Preparação e diagnóstico

## Ferramentas

Veja antes se `adb` e `fastboot` já existem. Se faltarem, avise que vai instalar no computador e peça permissão. Instale o Android SDK Platform-Tools, que traz os dois, a partir de fonte oficial:

- **Windows:** `winget install --id Google.PlatformTools -e`. O atalho no PATH pode exigir reabrir o terminal; se o comando não for encontrado, procure `adb.exe` em `%LOCALAPPDATA%\Microsoft\WinGet\Packages`.
- **macOS:** `brew install android-platform-tools`.
- **Linux:** `sudo apt install adb fastboot`, ou equivalente. Pode ser preciso configurar regras `udev`.

Se o aparelho aparecer com erro no modo Fastboot, falta driver. No Windows, instale o driver oficial do fabricante do aparelho, depois de pesquisar qual é. Para Motorola, por exemplo: `winget install --id Motorola.MobileDrivers -e`. Essa instalação pode pedir permissão de administrador.

**Samsung** não usa o modo Fastboot: o desbloqueio e a instalação passam pelo Download Mode, com Odin ou Heimdall, e pelo guia do modelo. O ADB continua valendo para diagnóstico, ajustes e limpeza.

## Localizar o aparelho

```text
adb devices -l
fastboot devices
```

- **Vários aparelhos:** pergunte qual é, pelo modelo. Use `-s <serial>` em todos os comandos a partir daí.
- **`unauthorized`:** a pessoa precisa desbloquear a tela e tocar em "Permitir". Não há como fazer isso remotamente.
- **Nada na lista:** peça para ativar a depuração USB tocando 7 vezes em "Número da versão" e ligando a opção em "Opções do desenvolvedor". Confira também se o cabo transmite dados e tente o modo de transferência de arquivos (MTP).
- **Windows:** quando o ADB não aparecer, `Get-PnpDevice -PresentOnly` ajuda a ver o que o sistema detecta.

## Diagnóstico

O script só lê informações e evita identificadores pessoais:

```text
adb -s <serial> push scripts/diagnose.sh /data/local/tmp/diagnose.sh
adb -s <serial> shell sh /data/local/tmp/diagnose.sh
adb -s <serial> shell rm /data/local/tmp/diagnose.sh
```

Interprete o resultado:

- **Pouca RAM (até 2 GB):** a memória costuma limitar mais que a CPU. Prefira limpar apps e reduzir processos.
- **Armazenamento quase cheio:** é uma causa comum de lentidão. Libere espaço, pedindo confirmação do que apagar.
- **Bateria com `health` ruim ou quente:** avise; um aparelho quente reduz a própria frequência.
- **Patch de segurança antigo:** verifique se há atualização oficial antes de considerar outra ROM.

## Medição de referência

`scripts/launch-bench.sh` abre cada app 3 vezes. Ele fecha os apps e pode interromper o que está em uso, então avise. Rode de forma destacada, porque uma queda do cabo não pode interromper o teste:

```text
adb -s <serial> push scripts/launch-bench.sh /data/local/tmp/launch-bench.sh
adb -s <serial> shell "nohup sh /data/local/tmp/launch-bench.sh com.android.settings com.whatsapp > /data/local/tmp/bench.out 2>&1 < /dev/null &"
adb -s <serial> shell cat /data/local/tmp/bench.out
```

Repita a última linha até aparecer `FIM`. Depois, remova os arquivos temporários:

```text
adb -s <serial> shell rm /data/local/tmp/launch-bench.sh /data/local/tmp/bench.out
```

Para comparar de forma justa:

- use os mesmos apps;
- espere o mesmo tempo depois de reiniciar;
- deixe o aparelho parado e com bateria semelhante;
- evite apps que abrem avisos em tela cheia, como a câmera, porque esses avisos atrapalham as medições seguintes.

A primeira abertura depois de reiniciar costuma ser muito mais lenta. Use a mediana.
