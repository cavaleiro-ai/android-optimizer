#!/system/bin/sh
# Read-only survey of the camera stack. Changes nothing on the device.
# Usage: adb -s <serial> shell sh /data/local/tmp/camera-scan.sh > camera-scan.txt
# Run it detached with nohup if the USB link is unstable. Ends with FIM.
# Personal data is left out: no serial, accounts or the camera usage log.

section() { echo; echo "== $1"; }

section DEVICE
echo "model $(getprop ro.product.manufacturer) $(getprop ro.product.model) ($(getprop ro.product.device))"
echo "android $(getprop ro.build.version.release) sdk $(getprop ro.build.version.sdk)"
echo "build $(getprop ro.build.type) $(getprop ro.lineage.version)"
echo "platform $(getprop ro.board.platform) abi $(getprop ro.product.cpu.abilist)"
echo "treble $(getprop ro.treble.enabled) vndk_lite $(getprop ro.vndk.lite)"

section CAMERA_SERVICE
dumpsys media.camera > /data/local/tmp/.camscan 2>/dev/null
grep -E "Number of camera devices|Device [0-9]+ maps to" /data/local/tmp/.camscan
# HAL version per device, facing and whether Camera2 is native or emulated.
grep -E "== Camera (HAL )?[Dd]evice|Device version|device@[0-9.]+/|Facing:|Orientation:|API2 not directly|API1 info|supportedHardwareLevel|android.info.supportedHardwareLevel" /data/local/tmp/.camscan | sed 's/^ *//' | head -n 60
section CAMERA2_CAPABILITIES
# Present only for HAL3 devices. Lists RAW, MANUAL_SENSOR, BURST_CAPTURE and so on.
grep -A3 -E "android.request.availableCapabilities|android.info.supportedHardwareLevel|android.sensor.info.physicalSize|android.sensor.info.pixelArraySize|android.lens.info.availableFocalLengths|android.control.availableVideoStabilizationModes|android.lens.info.availableOpticalStabilization" /data/local/tmp/.camscan | sed 's/^ *//' | head -n 80

section HAL1_PARAMETERS
# Present for HAL1 devices after any app opened the camera once.
grep -E "== Camera device [0-9]+ dynamic info|^[[:space:]]*(picture-size-values|video-size-values|preview-size-values|preview-fps-range-values|effect-values|scene-mode-values|iso-values|iso-mode-values|whitebalance-values|focus-mode-values|flash-mode-values|denoise-values|video-hfr-values|hfr-size-values|video-hsr-values|zsl-values|jpeg-quality|max-exposure-compensation|min-exposure-compensation|exposure-compensation-step|video-stabilization-supported|max-sharpness|max-contrast|max-saturation|chroma-flash-values|opti-zoom-values|af-bracket-values|ae-bracket-hdr-values|manual-exposure-modes|min-exposure-time|max-exposure-time|min-iso|max-iso)[:=]" /data/local/tmp/.camscan | sed 's/^[[:space:]]*//' | head -n 80
rm -f /data/local/tmp/.camscan

section SENSOR_MODELS
for d in /sys/class/video4linux/*; do
  n=$(cat "$d/name" 2>/dev/null)
  case "$n" in
    *imx*|*ov[0-9]*|*s5k*|*t4k*|*ar0*|*gc[0-9]*|*hi[0-9]*|*mt9*|*ov*|*sp[0-9]*) echo "$(basename "$d") $n" ;;
  esac
done
ls /vendor/lib /vendor/lib64 2>/dev/null | grep -iE '^libchromatix_|^libmmcamera_[a-z0-9]+\.so$|^com\.qti\.sensormodule|^libcamera_sensor' | sed 's/^/lib /' | sort -u | head -n 40

section VIDEO_PROFILES
for f in /vendor/etc/media_profiles_V1_0.xml /vendor/etc/media_profiles.xml /odm/etc/media_profiles_V1_0.xml /system/etc/media_profiles.xml; do
  [ -f "$f" ] || continue
  echo "file $f"
  # One line per profile (camera, quality, codec, size, fps, bitrate) and per encoder limit.
  awk 'function get(k,  m) { if (match($0, k "=\"[^\"]*\"")) { m = substr($0, RSTART + length(k) + 2, RLENGTH - length(k) - 3); return m } return "" }
       BEGIN { RS = "<" }
       /^CamcorderProfiles/ { print "camera " get("cameraId") }
       /^EncoderProfile/ { q = get("quality") }
       /^Video[ \t\r\n]/ { printf "  %s %s %sx%s %sfps %sbps\n", q, get("codec"), get("width"), get("height"), get("frameRate"), get("bitRate") }
       /^VideoEncoderCap/ { printf "encoder %s enabled=%s max %sbps up to %sx%s %sfps\n", get("name"), get("enabled"), get("maxBitRate"), get("maxFrameWidth"), get("maxFrameHeight"), get("maxFrameRate") }' "$f" | head -n 60
  break
done

section MOTION_SENSORS
dumpsys sensorservice 2>/dev/null | grep -oE 'android\.sensor\.(gyroscope|accelerometer|rotation_vector)\b' | sort | uniq -c

section CAMERA_APPS
cmd package query-activities -a android.media.action.STILL_IMAGE_CAMERA 2>/dev/null | grep -E 'packageName=' | sed 's/^ *//' | sort -u
cmd package query-activities -a android.media.action.VIDEO_CAMERA 2>/dev/null | grep -E 'packageName=' | sed 's/^ *//' | sort -u
pm list packages 2>/dev/null | grep -iE 'camera|snap|gcam|opencamera|gallery' | sed 's/^package://' | sort

section CAMERA_LIBRARIES
# Names only. Pull the ones of interest to the computer for camera-libs-scan.py.
for dir in /vendor/lib /vendor/lib64 /system/lib/hw /vendor/lib/hw /vendor/lib64/hw; do
  [ -d "$dir" ] || continue
  ls "$dir" 2>/dev/null | grep -iE 'camera|mmcamera|chromatix|camx|morpho|arcsoft|imglib|cac|ubifocus|optizoom|chromaflash|refocus|denoise|hdr' | sed "s|^|$dir/|"
done | sort | head -n 120

section CAMERA_PROPERTIES_SET
getprop | grep -iE 'camera|cam\.|vendor\.camera|persist\.vendor\.camera' | grep -viE 'init\.svc|boottime' | head -n 60

section STORAGE
df -h /data 2>/dev/null | tail -n 1

echo
echo FIM
