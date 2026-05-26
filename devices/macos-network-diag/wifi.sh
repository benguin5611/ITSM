#!/usr/bin/env bash
#
# wifi.sh — quick macOS wifi state check
#
# Run when you suspect wifi is the problem. ~5 seconds, captures the radio
# state (band, channel, RSSI, Tx rate, PHY mode) plus a fast throughput sample.
# Use this BEFORE toggling wifi off/on or doing anything else — those actions
# destroy the state we want to capture.
#
# Usage:
#   bash ~/Downloads/wifi.sh
#

set -u

OUT="$HOME/Downloads/wifi-diag-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$OUT") 2>&1

echo "Wifi state diagnostic — output: $OUT"
echo "Enter your Mac password if prompted."
echo

echo "===== wdutil info ====="
sudo wdutil info

echo
echo "===== Current SSID (en0) ====="
networksetup -getairportnetwork en0

echo
echo "===== airport -I (legacy tool, may be empty on macOS 15+) ====="
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I 2>/dev/null \
  || echo "(airport unavailable on this macOS version)"

echo
echo "===== Quick throughput sample (networkQuality) ====="
networkQuality -s 2>&1 | tail -10

echo
echo "Done. Output saved to $OUT"
echo
echo "What to look for in wdutil info:"
echo "  Band / Channel       2.4 GHz or channel 1/6/11   = bad radio choice"
echo "  RSSI                 worse than -70 dBm          = weak signal"
echo "  Tx Rate              single-digit Mbps           = degraded link"
echo "  PHY Mode             802.11n or worse            = not on modern radio"
