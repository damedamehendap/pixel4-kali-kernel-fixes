# Pixel 4 RTL8192EU fixes

Target: ARM64 Pixel 4, Linux 4.14.276-dirty, Clang r416183b, CFI/LTO/MODVERSIONS enabled.

`pixel4-driver.patch` is the complete local driver diff against Mange/rtl8192eu-linux-driver commit c629cc9. It includes platform/build compatibility changes and the CFI fix. `cfi-callback-fix.patch` is the CFI-only subset; do not apply both patches.

The tasklet wrappers use the kernel callback signature `void(unsigned long)` without incompatible function-pointer casts. The network transmit callback uses `netdev_tx_t`.

The original failed build used an incorrectly configured output directory. Build with a separate ARM64 output directory (`pixel4-out-rtl8192eu`) prepared from the matching kernel configuration and Module.symvers. The build script assumes the local toolchain and source directories shown in it. Existing kernel images were not modified.

## Optional automatic connection

`autoconnect/` contains the device-tested Magisk service and Kali supervisor. Set SOURCE to the existing saved home Wi-Fi profile and TARGET to the desired 2.4GHz SSID on the device. No credentials or real network identifiers are included here. This implementation requires the saved profile to expose a quoted passphrase; a raw SSID-specific PSK is not reusable.

Install service.sh and module.prop together with the matching built 8192eu.ko under `/data/adb/modules/rtl8192eu_autoconnect/`. Install autoconnect.py and executable dhcp-hook.sh in the Kali chroot at `/opt/rtl8192eu-autoconnect/`. The service expects `/data/local/nhsystem/kali-arm64` and waits for its existing proc/sys mounts. It does not mount or start NetHunter itself.

The supervisor manages only the external interface, its child processes, and routing table 19292 / rule priority 11992. It preserves Android's default network. Applications must explicitly select the external interface/source; this does not switch all Android or Kali traffic automatically.

## Verification

- Module build and callback CFI type verification passed.
- 205 imported symbol CRCs matched the existing kernel.
- Automatic insertion, WPA2 authentication, and DHCP succeeded.
- HTTPS explicitly bound to the external interface returned HTTP 200.
- Unplug/replug automatically reconnected and HTTPS again returned HTTP 200, without a device reboot.
- Boot startup is configured but a reboot test has not been performed.
- Tested module SHA256: 3b2f3b6c154b156376ed027e860682209dcc2e286555c72acacb72228545ab55.

This is a device-specific setup, not a general installer. No module binary, saved credentials, personal network identifiers, or raw device logs are included.
