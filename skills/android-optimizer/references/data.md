# Salvar e recuperar dados

Faça esta etapa **antes** de desbloquear o bootloader. O desbloqueio costuma apagar tudo, e depois pode não haver como recuperar. No caso real, a partição de dados ficou 100% zerada logo após o desbloqueio.

## Salvar o que existe

Pergunte o que importa, peça a confirmação de quem é o aparelho e salve em uma pasta escolhida pela pessoa:

```text
adb -s <serial> shell du -sh /storage/emulated/0/*
adb -s <serial> pull /storage/emulated/0/DCIM <pasta>
```

- Use `/storage/emulated/0/` ou inclua a barra no fim: `find /sdcard` não entra no atalho e retorna 0 arquivos, sem erro.
- WhatsApp e apps de 2FA têm backup próprio. Sem root, o ADB não acessa `/data/data`.
- Se houver conta Google e a pessoa quiser usar apps Google depois, oriente a remover a conta nas configurações antes de formatar, para evitar a trava FRP. Ela precisa saber a senha para usar essa conta depois.

## Recuperar arquivos apagados

Seja honesto: as chances são baixas. Só faça com o dono ou com autorização dele.

1. Peça para parar de usar o aparelho, porque gravações sobrescrevem dados.
2. Procure o que ainda existe: pastas ocultas, lixeiras e caches de galeria.
3. Sugira primeiro fontes externas, como Google Fotos, computador antigo, cartão microSD e conversas. Só o dono deve acessar as contas.
4. Sem root, não dá para copiar a memória interna. Um bootloader já desbloqueado permite abrir um recovery com `fastboot boot` e copiar a partição:
   ```text
   adb -s <serial> pull /dev/block/by-name/userdata userdata.img
   ```
   O caminho muda por aparelho. Confira se há espaço livre no PC.
5. Verifique a imagem antes de procurar: a partição pode estar criptografada, o que é o padrão em aparelhos modernos e torna a recuperação inviável, ou zerada. Compare o checksum com o do aparelho e procure assinaturas (`FF D8 FF`, `ftyp`) ou use o PhotoRec.

Trate as imagens como dados pessoais: não as envie a lugar nenhum, e apague quando terminar, com o acordo da pessoa.
