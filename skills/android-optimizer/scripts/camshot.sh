#!/system/bin/sh
# Taps the shutter and times how long until the photo is fully saved.
# Usage: sh camshot.sh <label> <folder> <x> <y> [timeout_s]
# Prints: RESULT <label> <seconds> <file> <bytes>, or TIMEOUT. Ends with FIM.
LABEL="$1"; DIR="$2"; X="$3"; Y="$4"; LIMIT="${5:-60}"
up() { cut -d' ' -f1 /proc/uptime; }
mkdir -p "$DIR" 2>/dev/null
BEFORE=$(ls "$DIR" 2>/dev/null | grep -ivE '\.(mp4|3gp)$' | wc -l)
T0=$(up)
input tap "$X" "$Y"
END=$(awk -v t="$T0" -v l="$LIMIT" 'BEGIN{print t+l}')
while :; do
  NOW=$(up)
  if awk -v a="$NOW" -v b="$END" 'BEGIN{exit !(a>b)}'; then echo "TIMEOUT $LABEL"; echo FIM; exit 1; fi
  COUNT=$(ls "$DIR" 2>/dev/null | grep -ivE '\.(mp4|3gp)$' | wc -l)
  if [ "$COUNT" -gt "$BEFORE" ]; then
    FILE=$(ls -t "$DIR" | grep -ivE '\.(mp4|3gp)$' | head -n 1)
    LAST=-1
    while :; do
      SIZE=$(stat -c %s "$DIR/$FILE" 2>/dev/null || echo 0)
      [ "$SIZE" -gt 0 ] && [ "$SIZE" = "$LAST" ] && break
      LAST="$SIZE"; sleep 0.3
    done
    T1=$(up)
    echo "RESULT $LABEL $(awk -v a="$T0" -v b="$T1" 'BEGIN{printf "%.2f", b-a-0.3}') $FILE $SIZE"
    echo FIM; exit 0
  fi
  sleep 0.1
done
