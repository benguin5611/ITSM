#!/usr/bin/env bash
#
# wifi.sh — quick macOS wifi state check
#
# Run when you suspect wifi is the problem. ~10 seconds for the basic checks,
# captures the radio state (band, channel, RSSI, Tx rate, PHY mode), a fast
# throughput sample, active network extensions (VPN clients / content
# filters), and DNS config. Also pulls the last hour's wifi fault counters
# and DNS-resolver-stall count from the unified log (needs sudo) — these
# catch an L2 datapath stall that still reports a healthy RSSI, which the
# basic tools above can't distinguish from a real disassociation.
#
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
echo "===== Active network extensions (VPN clients, content filters) ====="
echo "If DNS dies while the radio looks fine, check here first — a filter"
echo "extension sitting in the data path can stall traffic with zero radio symptoms."
systemextensionsctl list 2>&1 | grep -i "network" || echo "(none found / systemextensionsctl unavailable)"

echo
echo "===== DNS configuration (scutil --dns, first resolver) ====="
scutil --dns 2>&1 | awk '/^resolver #1/{f=1} f{print} f&&/^$/{exit}'

echo
echo "===== Recent sleep/wake/shutdown history (pmset) ====="
pmset -g log 2>&1 | tail -15

echo
echo "===== Reboot history ====="
last reboot 2>&1 | head -5

echo
echo "===== Quick throughput sample (networkQuality) ====="
networkQuality -s 2>&1 | tail -10

echo
echo "===== Wifi fault counters, last hour (requires sudo, unified log) ====="
echo "L2DatapathStallCount / SlowWiFiDnsFailure > 0 means the driver itself"
echo "flagged a stall — distinguishes a real driver/AP-side fault from an"
echo "app-level DNS problem, even when RSSI/noise/SNR above look perfectly healthy."
sudo /usr/bin/log show --last 1h \
  --predicate 'eventMessage contains "WiFiUsageSession" OR eventMessage contains "FaultReason"' 2>/dev/null \
  | grep -E "FaultReasonL2DatapathStallCount|FaultReasonSlowWiFiDnsFailure|FaultReasonDhcpFailure|FaultReasonArpFailure|FaultReasonBrokenBackhaulLinkFailed" \
  | grep -v "= 0;" \
  || echo "(no nonzero fault counters in the last hour, or sudo unavailable)"

echo
echo "===== DNS resolver stalls, last 30 min (requires sudo, unified log) ====="
STALL_COUNT=$(sudo /usr/bin/log show --last 30m \
  --predicate 'eventMessage contains "resolver:dns_stall" OR eventMessage contains "resolver:children_stall"' 2>/dev/null \
  | grep -c "resolver:")
echo "resolver:dns_stall / resolver:children_stall events: $STALL_COUNT"
echo "(a handful per 30min is normal background noise; a sustained burst of"
echo "10+ in a couple of minutes is the signature of a real DNS-path outage)"

echo
echo "Done. Output saved to $OUT"
echo
echo "What to look for in wdutil info:"
echo "  Band / Channel       2.4 GHz or channel 1/6/11   = bad radio choice"
echo "  RSSI                 worse than -70 dBm          = weak signal"
echo "  Tx Rate              single-digit Mbps           = degraded link"
echo "  PHY Mode             802.11n or worse            = not on modern radio"
echo
echo "If RSSI/Tx Rate/PHY Mode all look healthy but SSID check says"
echo "'not associated' and DNS is failing: that's an L2 datapath stall, not"
echo "a real disassociation. Check the fault counters and resolver-stall"
echo "count above, and check your router/AP's own log for the same window —"
echo "a mesh AP's backhaul can stall a client's data path while the client-to-AP"
echo "link itself stays perfectly healthy."
