# Limpeza de apps

## Como fazer

Liste os apps e separe por grupo:

```text
pm list packages -e      # ativos
pm list packages -d      # desativados
pm list packages -3      # instalados pela pessoa
dumpsys meminfo          # quem usa memória
```

Mostre a lista proposta em linguagem simples e peça aprovação antes. Use primeiro a opção mais fácil de desfazer:

| Ação | Comando | Como desfazer |
|---|---|---|
| Desativar | `pm disable-user --user 0 <pacote>` | `pm enable <pacote>` |
| Remover para o usuário | `pm uninstall -k --user 0 <pacote>` | `cmd package install-existing <pacote>` |

**Espere pelo menos 45 segundos e rode `sync` antes de reiniciar.** No caso real, reiniciar logo depois fez 12 desativações se perderem. Depois de reiniciar, confira com `pm list packages -d`.

Apps desativados continuam ocupando armazenamento, e às vezes um processo continua rodando até o próximo reinício. O ganho de memória costuma ser pequeno: no caso real, 12 apps renderam cerca de 20 MB. Diga isso à pessoa.

## Grupos

- **Normalmente seguros:** demonstrações, impressão (se não usa), protetores de tela, papéis de parede animados, jogos e apps de operadora.
- **Pergunte:** calculadora, relógio, galeria, câmera, rádio, telefone, contatos, mensagens, loja do fabricante e assistentes.
- **Não mexa:** `android`, `com.android.systemui`, `com.android.phone`, `com.android.settings`, `com.android.permissioncontroller`, `com.android.providers.*`, o único teclado, a única tela inicial, WebView, Google Play Services (se usa apps Google), alertas de emergência (`cellbroadcast*`), `com.android.emergency`, instalador de pacotes e serviços do fabricante ligados a rádio, câmera ou impressão digital.

Pacotes têm nomes diferentes por marca. Pesquise cada um antes de propor, por exemplo na lista do projeto Universal Android Debloater. Um nome conhecido não garante segurança em outro aparelho. Se o aparelho reiniciar sozinho ou não iniciar depois de mudanças, reative os últimos pacotes pelo ADB, se ele ainda responder. Se não responder, avise que pode ser preciso restaurar o aparelho.
