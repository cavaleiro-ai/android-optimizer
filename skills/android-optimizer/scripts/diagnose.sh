#!/system/bin/sh
# Somente leitura. Nao coleta serial, IMEI, contas nem dados de rede.

section() { echo; echo "--- $1"; }

section "aparelho"
for p in ro.product.manufacturer ro.product.model ro.product.device ro.build.version.release \
         ro.build.version.sdk ro.build.version.security_patch ro.build.display.id ro.bootloader \
         ro.boot.slot_suffix ro.boot.dynamic_partitions ro.crypto.state ro.crypto.type \
         ro.debuggable ro.config.low_ram sys.boot_completed; do
  echo "$p = $(getprop "$p")"
done
echo "ABI = $(getprop ro.product.cpu.abilist)"

section "kernel"
uname -r 2>/dev/null

section "cpu"
grep -E 'Hardware|model name' /proc/cpuinfo | sort -u
echo "nucleos = $(grep -c ^processor /proc/cpuinfo)"
for c in /sys/devices/system/cpu/cpufreq/policy* /sys/devices/system/cpu/cpu0/cpufreq; do
  [ -d "$c" ] || continue
  echo "$c: max=$(cat "$c/cpuinfo_max_freq" 2>/dev/null) atual=$(cat "$c/scaling_cur_freq" 2>/dev/null) governor=$(cat "$c/scaling_governor" 2>/dev/null)"
done

section "gpu"
for f in max_gpuclk gpu_available_frequencies; do
  [ -r "/sys/class/kgsl/kgsl-3d0/$f" ] && echo "$f = $(cat "/sys/class/kgsl/kgsl-3d0/$f")"
done
ls /sys/class/devfreq/ 2>/dev/null

section "memoria"
grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree' /proc/meminfo
dumpsys meminfo 2>/dev/null | grep -E 'Free RAM|Used RAM|Lost RAM|Tuning'

section "armazenamento"
df -h /data 2>/dev/null | tail -1

section "bateria"
dumpsys battery 2>/dev/null | grep -E 'level|health|temperature|status'

section "maiores usos de memoria"
dumpsys meminfo 2>/dev/null | sed -n '/Total PSS by process/,/Total PSS by OOM/p' | head -20

section "apps"
echo "total = $(pm list packages | wc -l)"
echo "ativos = $(pm list packages -e | wc -l)"
echo "desativados = $(pm list packages -d | wc -l)"
echo "instalados pela pessoa = $(pm list packages -3 | wc -l)"

section "configuracoes"
for k in "global window_animation_scale" "global transition_animation_scale" \
         "global animator_duration_scale" "global wifi_scan_always_enabled" \
         "global ble_scan_always_enabled" "global bluetooth_on" \
         "global activity_manager_constants" "secure doze_enabled" "secure doze_always_on" \
         "system haptic_feedback_enabled" "system sound_effects_enabled" "system screen_off_timeout"; do
  echo "$k = $(settings get $k 2>/dev/null)"
done

section "carga"
uptime
