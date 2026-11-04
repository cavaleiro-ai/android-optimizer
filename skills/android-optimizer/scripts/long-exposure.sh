#!/system/bin/sh
# Long exposure through Motorola's sensor debug override (mm-camera2 phones).
# Usage: sh long-exposure.sh <milliseconds> <gain> [photo_folder]
#   Example: sh long-exposure.sh 850 4
# Open Camera must be open on screen, with the volume key set to take photos
# (its default). The phone must rest on something: at 850 ms any movement blurs.
# Always switches the override off at the end, even on errors. Ends with FIM.
#
# Tested only on a Moto G 2014 (IMX179, LineageOS 17.1): the sensor really
# exposed 850 ms (64046 lines in the camera log). The sensor register holds
# 65535 lines, so stay below about 0.85 s there. Check other phones first with
#   grep -c persist.camera.mot_exp /vendor/lib/libmmcamera2_sensor_modules.so
# and confirm the sensor name is in that library's list (camera-libs-scan.py).
# The photo's EXIF keeps the automatic values, not the forced ones.
MS="$1"; GAIN="$2"; DIR="${3:-/sdcard/DCIM/OpenCamera}"
LIB=/vendor/lib/libmmcamera2_sensor_modules.so

reset() { setprop persist.camera.motexp_update 0 2>/dev/null; }
trap reset EXIT INT TERM

if [ -z "$MS" ] || [ -z "$GAIN" ]; then
  echo "ERRO: informe milissegundos e ganho, por exemplo: sh long-exposure.sh 850 4"; echo FIM; exit 1
fi
if ! grep -q persist.camera.mot_exp "$LIB" 2>/dev/null; then
  echo "ERRO: este aparelho nao tem o recurso de exposicao da Motorola ($LIB)."; echo FIM; exit 1
fi
if ! setprop persist.camera.motexp_update 0 2>/dev/null; then
  echo "ERRO: o shell nao pode gravar persist.camera.* neste sistema."; echo FIM; exit 1
fi

count() { ls "$DIR" 2>/dev/null | grep -ic '\.jpg$'; }
BEFORE=$(count)
setprop persist.camera.use_realexp 1
setprop persist.camera.mot_gain "$GAIN"
setprop persist.camera.mot_exp "$MS"
setprop persist.camera.motexp_update 1
# Give the sensor a few frames at the new exposure.
WAIT=$(( (MS * 4 + 999) / 1000 )); [ "$WAIT" -lt 3 ] && WAIT=3
sleep "$WAIT"
input keyevent 24
i=0
while [ "$i" -lt 40 ] && [ "$(count)" -le "$BEFORE" ]; do sleep 1; i=$((i + 1)); done
sleep 2
reset
if [ "$(count)" -gt "$BEFORE" ]; then
  echo "FOTO $DIR/$(ls -t "$DIR" | grep -i '\.jpg$' | head -n 1)"
else
  echo "ERRO: nenhuma foto nova em 40 s. O Open Camera estava aberto na tela?"
fi
logcat -d -t 400 2>/dev/null | grep 'MOT GAIN' | tail -n 1
echo "motexp_update=$(getprop persist.camera.motexp_update)"
echo FIM
