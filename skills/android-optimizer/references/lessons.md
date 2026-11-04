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

## Câmera

Do caso descrito em `docs/estudo-de-caso-camera-moto-g-2014.md`:

| Situação | O que deu errado | O que fazer |
|---|---|---|
| HDR por hardware do app original | Travou a câmera por mais de 90 s sem gerar foto | Teste cada modo antes de recomendar e deixe desligado o que travar |
| Câmera lenta de 90 e 120 fps no menu | Capturavam uns 30 fps: o adaptador de câmera da ROM anunciava modos inexistentes | Conte quadros contra o tempo real antes de prometer fps |
| Fotos de teste com o celular deitado | A orientação ficou indefinida e as fotos saíram de lado | Teste com o celular de pé ou de lado, apoiado |
| Qualidade JPEG em 100% | O driver ignorou o pedido, e a tabela de compressão ficou igual à do app original | Confira a tabela de quantização da foto antes de dizer que melhorou |
| Primeira vez no modo HDR do Open Camera | Uma explicação na tela recebeu o toque do disparo | Toque em OK e repita o disparo |
| Restore settings do Open Camera | A lista começa com "Parent Folder", e o toque abriu outro arquivo | Leia as posições na tela antes de tocar |
| `grep` simples na saída do `uiautomator` | Textos e posições ficaram desalinhados | Leia nó por nó, juntando `text` e `bounds` do mesmo elemento |
| Visitar o menu de vídeo do app original | O app ficou em modo vídeo, e o toque seguinte iniciou uma gravação | Volte o app ao modo foto e confira o ícone antes de disparar |
| Toque para parar uma gravação | Às vezes não pegou, e o vídeo continuou | Confira se o arquivo terminou (`ffprobe` ou `mp4info.py`) |
| `pkill -f <script>` pelo `adb shell` | Matou o próprio shell, porque o nome estava na linha de comando | Use `pgrep -f 'nom[e]'` e mate pelo PID |
| Bibliotecas de recursos instaladas | Carregaram, mas o driver nunca lia as chaves que ligam o recurso | Rode `camera-libs-scan.py refs` antes de instalar |
| Mudança no driver sem efeito | O processo que carrega o driver (`mediaserver`) guardava a lista antiga | Reinicie também esse processo |
| Desligar Rooted debugging com `input tap` | A opção não mudou | Use `keyevent 20` até a linha e `keyevent 23`, e confira com `service call adbroot_service 2` |
| Testar se o root estava bloqueado rodando `adb root` | Com a opção ainda ligada, o ADB voltou a ser root | Confira com `service call adbroot_service 2`, que só lê |
| Copiar bibliotecas baixadas para o sistema | O Claude Code bloqueou a ação | Não contorne: explique e deixe a pessoa decidir |
| Exposição forçada | A foto continuou com 1/15 s e ISO 1250 no EXIF | Confie no log do driver (`LINECOUNT`) e no brilho medido |

## Windows e PowerShell

- Prefira `cmd /c` ou `adb exec-out` para saída binária, porque o redirecionamento do PowerShell 5.1 pode corrompê-la.
- `2>&1` em comandos nativos pode marcar sucesso como erro no PowerShell 5.1.
- Grave scripts enviados ao aparelho com fim de linha LF, não CRLF.
- Em comandos com `$`, use aspas simples ou escape, e confira o que chegou ao aparelho.

## Comunicação

- "Bloqueado" pode ser entendido como tela travada. Explique "bootloader" antes de usar a palavra.
- A pessoa pode achar que precisa do e-mail antigo. O código da Motorola vai para a conta que ela usar no site, não para a conta registrada no aparelho.
- Diga sempre o que precisa dela, em passos curtos, e o que ela não deve fazer durante a operação.
