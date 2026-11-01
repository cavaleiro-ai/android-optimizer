# Desbloqueio do bootloader e recovery

## Antes

Confirme que o aparelho é da pessoa ou que ela tem autorização do dono. Desbloquear para escapar de uma trava de conta em aparelho alheio é um contorno não permitido.

Confirme também que a pessoa entendeu que:

- os dados provavelmente serão apagados;
- a garantia pode ser perdida;
- apps de banco, carteiras digitais e conteúdo protegido podem parar de funcionar;
- um erro pode deixar o aparelho sem ligar.

Confira ainda:

- dados salvos ([data.md](data.md));
- bateria acima de 60%;
- cabo confiável.

Não use ferramentas pagas ou "desbloqueadores" de terceiros: costumam trazer malware e podem danificar o aparelho.

## Marcas

Estas regras mudam com frequência e variam por modelo, região e operadora, e parte delas vem de blogs e fóruns. **Pesquise a regra atual do modelo exato antes de orientar.**

| Marca | Situação geral | Observação |
|---|---|---|
| Google Pixel | Oficial e simples | Opção "Desbloqueio OEM" + `fastboot flashing unlock`. Modelos de operadora podem bloquear |
| Motorola | Varia | `fastboot oem get_unlock_data`, código por e-mail no site da Motorola, `fastboot oem unlock <código>`. Muitos modelos de operadora são bloqueados |
| OnePlus | Geralmente por fastboot | Regras mais rígidas para modelos chineses recentes com ColorOS |
| Nothing | Normalmente por fastboot | Confirme o modelo |
| Xiaomi / Redmi / POCO | Restrito | Exige autorização pelo app da Xiaomi e tempo de espera. Na China, muito limitado. Cuidado com anti-rollback |
| Samsung | Muito restrito | Usa Odin/Heimdall, não fastboot. Desbloqueio queima o Knox de forma permanente. Relatos de remoção da opção na One UI 8, sem confirmação clara da Samsung. Modelos Snapdragon dos EUA e Canadá nunca foram desbloqueáveis |
| Sony | Consultar | Não confirmei a situação atual. Pode perder chaves DRM |
| Huawei | Sem caminho oficial | A empresa parou de fornecer códigos |
| ASUS, vivo, iQOO, Realme, OPPO | Geralmente sem caminho ou muito restrito | Consulte o modelo |

Se não houver caminho oficial, diga isso e volte aos níveis sem desbloqueio. Não tente explorar falhas.

## Passo a passo (aparelhos com fastboot)

1. Ative "Desbloqueio OEM" nas opções do desenvolvedor, quando existir.
2. Entre no modo: `adb -s <serial> reboot bootloader`, ou desligue e segure a combinação de botões do modelo.
3. Confirme a detecção com `fastboot devices`. Se falhar, veja os drivers.
4. Leia o estado e filtre a saída, porque `getvar all` pode trazer IMEI:
   ```text
   fastboot -s <serial> getvar unlocked
   fastboot -s <serial> getvar securestate
   fastboot -s <serial> flashing get_unlock_ability
   ```
5. **Confirme explicitamente e só então** rode o comando da marca:
   - 2015 em diante: `fastboot -s <serial> flashing unlock`.
   - Antigos: `fastboot -s <serial> oem unlock`.
   - O aparelho costuma pedir confirmação na tela.
6. Confira `unlocked: yes` ou equivalente.

Nunca bloqueie de novo com ROM personalizada instalada, porque isso pode impedir o aparelho de ligar. Só bloqueie após voltar ao sistema oficial completo.

## Recovery

Use o recovery indicado pela ROM escolhida (TWRP, Lineage Recovery etc.), sempre feito para o codinome exato do aparelho (`ro.product.device` e a tabela da ROM). Baixe de fonte oficial e confira o checksum.

**Teste antes de gravar, quando possível:**

```text
fastboot -s <serial> boot recovery.img
```

Gravar conforme o guia do aparelho. Em aparelhos com partição `recovery`, é normalmente:

```text
fastboot -s <serial> flash recovery recovery.img
```

Atenção ao tipo do aparelho:

- **Sem partição recovery:** vai em `boot` ou `vendor_boot`. Slots A/B também mudam o processo.
- **Partições dinâmicas:** podem exigir `fastboot reboot fastboot` (fastbootd).
- **`vbmeta`:** só altere se o guia do aparelho mandar.
- **Antirrollback:** não instale firmware mais antigo sem confirmar que é permitido.
- **Samsung:** siga o guia com Odin/Heimdall.

Use sempre o guia específico do aparelho quando houver. Este resumo não o substitui.
