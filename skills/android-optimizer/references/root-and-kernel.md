# Root, modo desempenho e overclock

**Importante:** o caso real que originou a skill parou nas opções. Nada aqui foi executado naquele aparelho, então trate como guia e valide em cada modelo.

## Antes

Confirme que a pessoa entendeu:

- apps de banco, carteiras e alguns jogos podem detectar e recusar;
- o aparelho fica mais exposto a malware;
- mais frequência significa mais calor, menos bateria e desgaste;
- uma bateria antiga ou com defeito torna isso perigoso.

**Bateria:** o `health` do Android não detecta inchaço. Pergunte se a traseira está estufada, a tela levantando ou o aparelho aquecendo sem uso, e pesquise problemas e recalls de bateria do modelo. Se houver sinal de problema, não prossiga.

Faça uma etapa por vez. Peça confirmação para cada kernel. As frequências podem ser autorizadas por faixa, desde que combine antes o limite e os critérios de parada.

Se a pessoa pedir "o máximo", suba por passos até a primeira falha ou até a temperatura-limite e fique no último valor estável. Pergunte antes se ela aceita o trabalho de compilar um kernel, pois pode não existir um pronto.

## Root

- **Mais comum:** Magisk, com a imagem `boot` exata do sistema instalado, seguindo a documentação oficial.
- **ROM de depuração:** algumas têm "Depuração com root" nas opções do desenvolvedor (`adb root`).

Com imagem `boot` errada, o aparelho pode não ligar. Guarde a imagem original.

## Modo desempenho (sem overclock)

Mantém as frequências oficiais mais altas, sem ultrapassar os limites do chip. Primeiro leia os valores e anote:

```text
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
ls /sys/class/devfreq/
cat /sys/class/devfreq/*/governor
```

Depois, como root:

```text
echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo performance > /sys/class/devfreq/<gpu>/governor
```

Essas mudanças somem ao reiniciar, o que facilita testar. Os caminhos variam por chip. Em aparelhos com grupos de núcleos, aplique a cada grupo. Meça com `launch-bench.sh` e acompanhe a bateria e a temperatura. O ganho no dia a dia pode ser pequeno.

Só torne permanente, por exemplo com um módulo Magisk, depois de medir ganho real.

## Kernel e overclock

Avise que costuma exigir compilar um kernel específico, e que o kernel oficial normalmente não permite frequências acima do padrão.

1. Pesquise um kernel mantido, para o modelo e a versão do Android exatos. Muitos fóruns avisam que kernels personalizados não têm suporte nas ROMs.
2. Se não existir, compile a partir do código da ROM. Isso exige ambiente Linux, ajuste da tabela de frequências e tensões e conhecimento de kernel. Se a pessoa não quiser investir nisso, pare.
3. **Teste sem gravar:** `fastboot -s <serial> boot kernel-teste.img`. Se travar, basta reiniciar.
4. Suba pouco (por volta de 5% a 10%, como ponto de partida a validar), com testes de estresse e leitura de temperatura. Pare se a bateria passar de cerca de 45 °C ou houver travamentos e artefatos.
5. Grave de forma permanente só depois de dias estáveis, com a imagem original guardada.

Recordes de benchmark mostram o limite por curtos períodos, não a estabilidade para o uso diário.

**GPU:** segue o mesmo processo, mas costuma ter pouca documentação.

**RAM:** não recomende. A frequência depende de firmware e controlador; erros podem corromper dados. Ajustes de ZRAM e `swappiness` são gestão de memória, não overclock.

**Temperatura:** não desative limites térmicos nem `thermal-engine`. Eles protegem o aparelho e as pessoas.
