# Lições de falhas reais

Cada item aconteceu no caso real descrito em `docs/estudo-de-caso-moto-g-2014.md`, no repositório da skill.

| Situação | O que deu errado | O que fazer |
|---|---|---|
| Vários aparelhos no USB | O tablet da pessoa apareceu junto com o celular | Use sempre `-s <serial>` e confirme qual é o alvo |
| `find /sdcard` | O caminho é um atalho, e o resultado de 0 arquivos parecia verdadeiro | Use `/storage/emulated/0/` |
| Recuperação depois do desbloqueio | A partição já estava 100% zerada | Salve os dados antes e deixe claro que pode ser tarde demais |
| `pm disable-user` + reinício imediato | As 12 desativações se perderam | Espere 45 s, rode `sync` e confira depois de reiniciar |
| `twrp wipe data` | Formatou também o cache, apagando a ROM enviada, e o TWRP travou | Envie a ROM depois, e reinicie o recovery se ele travar |
| `twrp format data` | Comando desconhecido nessa versão | Confirme comandos no aparelho, com `twrp` e a documentação da versão |
| `speed` em app grande | Travou por RAM | Use `speed-profile` |
| `ro.config.low_ram` | Ficou mais lento | Meça sempre e desfaça |
| `input text` com aspas no PowerShell | Digitou 2 caracteres a mais na senha | Confira o campo sem exibir o conteúdo |
| Benchmark preso ao cabo | Uma queda USB cancelou o teste | Rode com `nohup` no aparelho |
| Câmera no benchmark | O aviso em tela cheia atrapalhou | Evite apps com avisos em tela cheia |
| Máscara de dados com `sed` | Um e-mail apareceu na saída | Não liste contas se não precisar |
| Valor original não anotado | O tempo de tela não pôde ser restaurado com certeza | Anote tudo antes de mudar |
| Driver de Fastboot | `fastboot devices` vazio com aparelho em erro no Windows | Veja o gerenciador de dispositivos e instale o driver do fabricante |
| Sistema novo sem ADB | Parecia falha, mas estava funcionando | Olhe a tela e o tipo de dispositivo USB |
| Windows oferecendo formatar um disco de 0 bytes | O aparelho apareceu como disco vazio | Oriente a recusar |
| Arquivo `.zip` que não abre | Era um 7z com a extensão trocada, não um arquivo danificado | Leia os primeiros bytes antes de concluir |
| Captura de tela durante a medição | Criou uma travada de cerca de 250 ms, que parecia ser do jogo: 58,5 FPS em vez de 59,89 | Capture só depois de medir |
| Vídeo ou menu como teste de emulador | Exigem bem menos que uma cena 3D | Meça uma cena 3D, com a mesma sequência |
| Editar `retroarch.cfg` com o app aberto | O RetroArch regrava o arquivo ao sair | Use `am force-stop`, edite e só depois abra |
| Copiar o núcleo pelo ADB | A pasta do app é privada, e o `run-as` falha | Use o menu "Install or Restore a Core", com o `.so` na pasta de `core_assets_directory` |
| Medir com a tela bloqueada | O app não aparece nas camadas, e o script não encontra nada | Desbloqueie com `input keyevent 82` e confirme o foco |
| `keyevent 82` com a tela já desbloqueada | Abriu a aba de notificações por cima | Tire uma captura antes de tocar na tela |
| Quedas do USB em captura de tela | O PNG chegou cortado e não abriu | Confira se o arquivo termina em `IEND` e tire de novo |

## Windows e PowerShell

- Prefira `cmd /c` ou `adb exec-out` para saída binária, porque o redirecionamento do PowerShell 5.1 pode corrompê-la.
- `2>&1` em comandos nativos pode marcar sucesso como erro no PowerShell 5.1.
- Grave scripts enviados ao aparelho com fim de linha LF, não CRLF.
- Em comandos com `$`, use aspas simples ou escape, e confira o que chegou ao aparelho.

## Comunicação

- "Bloqueado" pode ser entendido como tela travada. Explique "bootloader" antes de usar a palavra.
- A pessoa pode achar que precisa do e-mail antigo. O código da Motorola vai para a conta que ela usar no site, não para a conta registrada no aparelho.
- Diga sempre o que precisa dela, em passos curtos, e o que ela não deve fazer durante a operação.
