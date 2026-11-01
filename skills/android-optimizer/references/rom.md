# Troca do sistema (ROM)

## Antes

Confirme que o aparelho é da pessoa ou que ela tem autorização do dono. Instalar outra ROM para fugir de FRP ou de bloqueio em aparelho alheio não é permitido.

## Escolher com honestidade

Pesquise o codinome do aparelho (`ro.product.device`) e busque, nesta ordem:

1. Atualização oficial do fabricante.
2. ROM oficial e mantida, como a [lista do LineageOS](https://wiki.lineageos.org/devices/) e outras com suporte ao modelo.
3. Build não oficial recente, de autor com histórico público.

O mais novo nem sempre é o melhor: em hardware antigo, um Android recente pode ficar mais pesado. Se existir uma ROM bem mais nova, explique a diferença e deixe a pessoa escolher.

Antes de baixar, verifique e informe:

- modelo e variante compatíveis (alguns modelos do mesmo codinome têm rádios diferentes);
- exigências de firmware, recovery e partições;
- data do build e data do patch de segurança;
- problemas relatados, como chip duplo, câmera, chamadas e notificações;
- situação de apps do Google e se a partição do sistema tem espaço para eles.

Builds abandonados e não oficiais ficam sem correções de segurança. Recomende não usar esses aparelhos para banco e contas importantes.

## Verificar o arquivo

Baixe em uma pasta nova, confira o checksum quando houver e inspecione o conteúdo sem executar nada:

- `META-INF/com/android/metadata`: `pre-device`, `pre-bootloader`, `post-sdk-level`, `post-security-patch-level`.
- `META-INF/com/google/android/updater-script`: as verificações `assert(getprop(...))`.

Compare com `ro.product.device` e `ro.bootloader` lidos do aparelho. Se o modelo não constar, pare. Não remova as verificações do script para forçar a instalação, porque elas evitam gravar a ROM errada.

Quando não houver checksum publicado, diga que a integridade não foi verificada.

## Instalar

Antes, **confirme explicitamente que tudo será apagado**, e **siga o guia oficial do aparelho quando houver**. Ele vale mais que os resumos abaixo. Veja o tipo do aparelho com `scripts/diagnose.sh` (`ro.boot.slot_suffix` e `ro.boot.dynamic_partitions`).

### Aparelhos com slots A/B ou sem partição recovery

Comum em aparelhos mais novos, como Pixel. Em geral, o fluxo do guia da ROM é:

1. Gravar o recovery indicado na partição indicada (`boot`, `recovery` ou `vendor_boot`) e, se o guia pedir, as imagens adicionais.
2. Reiniciar no recovery e confirmar o estado com `adb devices`.
3. Fazer o "Factory reset" no menu do recovery.
4. Instalar por `adb sideload <arquivo.zip>` e seguir o guia sobre o outro slot.
5. Só depois reiniciar.

Nesses aparelhos, não use os comandos `twrp` nem instruções de outros modelos sem confirmar.

### Aparelhos com TWRP e partição recovery

1. Abra o recovery e confirme com `adb devices` que o estado é `recovery`.
2. Se quiser poder voltar, faça backup das partições pelo recovery e copie para o PC.
3. Limpe conforme o guia da ROM. No TWRP via ADB, `twrp wipe cache` e `twrp wipe dalvik` são comuns. Em alguns aparelhos, `twrp wipe data` também formata o cache.
4. **Envie a ROM só depois de formatar**, e confira o checksum no aparelho (`sha256sum`).
5. Instale: `twrp install <arquivo.zip>`, ou `adb sideload <arquivo.zip>` no modo de sideload. Confirme que apareceu `script succeeded`.
6. Remova o arquivo e reinicie.

Com partição de dados zerada ou sem sistema de arquivos, o TWRP pode não montar e travar. Só formate diretamente se o caminho for confirmado (`readlink /dev/block/.../by-name/userdata`) e se o tamanho incluir a reserva de 16 KB usada em aparelhos antigos, por exemplo: `make_ext4fs -l <tamanho-16384> -a /data <particao>`. Confirme a montagem depois.

## Primeira inicialização

Pode demorar vários minutos. O ADB costuma vir desligado no sistema novo, então um aparelho sem ADB não significa falha: se o Windows mostrar transferência de arquivos, o Android provavelmente abriu. Peça para a pessoa olhar a tela. Se ficar no logo por mais de 15 a 20 minutos, considere travado: volte ao recovery com os botões.

Depois da configuração inicial, peça para ativar a depuração USB e confirme:

```text
getprop sys.boot_completed
getprop ro.lineage.version
getprop ro.build.version.release
getprop ro.build.version.security_patch
```

Confirme pelo menos Wi-Fi, chamadas, dados móveis e chips, câmera, som, GPS e sensores. O que não der para testar pelo ADB, diga à pessoa para testar.

## Sem Play Store

Instale apps pelo site oficial do desenvolvedor, com download direto, ou pelo F-Droid. Exemplos que funcionaram no caso real: `https://www.whatsapp.com/android/` e `https://telegram.org/dl/android/apk`.

Avise que eles não se atualizam sozinhos sem loja e que apps podem alertar sobre o uso de ROM personalizada. Antes de registrar um número no WhatsApp em um novo aparelho, explique que isso pode desconectar outro celular.
