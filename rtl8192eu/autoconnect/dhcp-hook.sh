#!/bin/sh
umask 077
case "$reason" in
 BOUND|RENEW|REBIND|REBOOT)
  printf '%s\n%s\n' "$new_ip_address" "$new_routers" > /run/rtl8192eu-autoconnect/lease.new
  mv /run/rtl8192eu-autoconnect/lease.new /run/rtl8192eu-autoconnect/lease
 ;;
 EXPIRE|FAIL|STOP|RELEASE) rm -f /run/rtl8192eu-autoconnect/lease ;;
esac
