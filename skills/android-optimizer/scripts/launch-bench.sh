#!/system/bin/sh
# Mede o tempo de abertura em ms: fecha e abre cada app, 3 vezes. Termina com FIM.
# Uso: sh launch-bench.sh com.android.settings com.whatsapp

[ $# -gt 0 ] || { echo "Informe ao menos um pacote"; echo FIM; exit 1; }

input keyevent KEYCODE_WAKEUP
wm dismiss-keyguard 2>/dev/null
sleep 2

for p in "$@"; do
  a=$(cmd package resolve-activity --brief -c android.intent.category.LAUNCHER "$p" | tail -1)
  case "$a" in
    */*) ;;
    *) echo "$p: sem tela inicial"; continue ;;
  esac
  r=""
  for i in 1 2 3; do
    am force-stop "$p"
    sleep 2
    t=$(am start -W -n "$a" 2>/dev/null | grep TotalTime | awk '{print $2}')
    r="$r ${t:-erro}"
    sleep 4
    input keyevent KEYCODE_HOME
    sleep 2
  done
  echo "$p:$r"
done

echo "--- memoria"
dumpsys meminfo | grep -E 'Free RAM|Used RAM'
dumpsys battery | grep temperature
uptime
echo FIM
