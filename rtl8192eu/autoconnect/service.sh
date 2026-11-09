#!/system/bin/sh
MODDIR=${0%/*}
KALI=/data/local/nhsystem/kali-arm64
STORE=/data/misc/apexdata/com.android.wifi/WifiConfigStore.xml
umask 077
# Wait for Android boot and the user's existing NetHunter mounts; do not remount them.
while [ "$(getprop sys.boot_completed)" != 1 ]; do sleep 10; done
while [ ! -r "$STORE" ] || [ ! -d "$KALI/proc/self" ] || [ ! -d "$KALI/sys/class/net" ]; do
 [ -f "$MODDIR/disable" ] && exit 0
 sleep 10
done
[ -f "$MODDIR/disable" ] && exit 0
[ "$(uname -r)" = 4.14.276-dirty ] || exit 1
if ! grep -q '^8192eu ' /proc/modules; then
 insmod "$MODDIR/8192eu.ko" || exit 1
fi
# The saved secret stays on the device and is passed through a pipe, not logged.
cat "$STORE" | chroot "$KALI" /usr/bin/python3 /opt/rtl8192eu-autoconnect/autoconnect.py >> "$MODDIR/service.log" 2>&1
