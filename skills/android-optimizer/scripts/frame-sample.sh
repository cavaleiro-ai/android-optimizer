#!/system/bin/sh
# Samples frame timing of the app in the foreground. Read-only.
# Usage: sh frame-sample.sh <package> [samples] [screenshot-path]
# Run it detached with nohup, send the output to a file and wait for FIM.
# Summarize the file on the computer with frame-stats.py.
PKG="$1"
SAMPLES="${2:-8}"
SHOT="$3"

if [ -z "$PKG" ]; then
  echo "ERRO: informe o pacote"
  echo FIM
  exit 1
fi

# The layer that holds the frames depends on the Android version, so try every
# layer of the app and keep the one with the most timestamps.
CANDIDATES=$(dumpsys SurfaceFlinger --list | grep "$PKG" | grep -v AppWindowToken)
LAYER=""
BEST=-1
OLD_IFS="$IFS"
IFS='
'
for CANDIDATE in $CANDIDATES; do
  COUNT=$(dumpsys SurfaceFlinger --latency "$CANDIDATE" 2>/dev/null | grep -cE '^[0-9]+[[:space:]]+[1-9]')
  if [ "$COUNT" -gt "$BEST" ]; then
    BEST="$COUNT"
    LAYER="$CANDIDATE"
  fi
done
IFS="$OLD_IFS"
if [ -z "$LAYER" ]; then
  echo "ERRO: nenhuma camada encontrada para $PKG. A tela esta desbloqueada e o app esta visivel?"
  echo FIM
  exit 1
fi

echo "LAYER $LAYER"
echo "TEMP_START $(dumpsys battery | grep ' temperature')"
echo "CPU_START $(grep -E '^cpu ' /proc/stat)"
i=0
while [ "$i" -lt "$SAMPLES" ]; do
  echo "SAMPLE $i"
  dumpsys SurfaceFlinger --latency "$LAYER" 2>/dev/null
  i=$((i + 1))
  sleep 1
done
echo "CPU_END $(grep -E '^cpu ' /proc/stat)"
echo "TEMP_END $(dumpsys battery | grep ' temperature')"
echo "RES $(top -b -n 1 | grep "$PKG" | head -n 1)"
# The screenshot comes last: on the test phone it froze the screen for about
# 250 ms, which would count as a stutter if taken while sampling.
if [ -n "$SHOT" ]; then
  screencap -p "$SHOT"
fi
echo FIM
