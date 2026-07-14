#!/usr/bin/env bash
#
# slow.sh — comprehensive macOS network diagnostic
#
# Run when something feels slow RIGHT NOW. ~90 seconds. Captures wifi state,
# routing, latency at each hop, DNS timing, and (the important bit) parallel
# packet captures on wifi vs any active VPN tunnel — so you can tell whether
# the bottleneck is the host stack, the wifi radio, the tunnel, or upstream.
#
# Run this BEFORE toggling wifi, rebooting, or restarting the VPN client.
# Those actions destroy the state we need.
#
# Usage:
#   bash ~/Downloads/slow.sh
#
# Reading the output (decision tree):
#   wdutil shows 2.4 GHz / weak RSSI / low Tx rate     -> wifi radio issue
#   Gateway ping bad, internet pings also bad          -> wifi/LAN
#   Gateway ping fine, public pings bad                -> ISP or upstream
#   TCP packets on the VPN utun during the curl        -> traffic IS tunnelled
#   TCP on en0 but throughput bad, wifi state fine     -> host stack issue
#   DNS query time > 500 ms                            -> resolver problem
#   Traceroute dies at hop 2-3                         -> ISP edge

set -u

OUT="$HOME/Downloads/slow-diag-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$OUT") 2>&1

banner() { echo; echo "===== $* ====="; }

echo "Slow-network diagnostic — output: $OUT"
echo "Requesting sudo (needed for tcpdump and wdutil)..."
sudo -v || { echo "sudo required"; exit 1; }

( while true; do sudo -n true; sleep 30; kill -0 "$$" 2>/dev/null || exit; done ) 2>/dev/null &
KEEPALIVE=$!
trap 'kill $KEEPALIVE 2>/dev/null' EXIT

# --- 1. Wifi radio state ---
banner "1. Wifi radio state (wdutil)"
sudo wdutil info

banner "2. Current SSID + BSSID"
networksetup -getairportnetwork en0
ipconfig getsummary en0 2>/dev/null | grep -E "SSID|BSSID|Channel|Security" || true

# --- 3. Tunnel detection (Twingate, Tailscale, anything in 100.64/10) ---
banner "3. Active VPN tunnel detection"
VPN_UTUN=$(ifconfig | awk '/^utun/{n=$1; sub(":","",n)} /inet 100\./{print n; exit}')
echo "Tunnel utun: ${VPN_UTUN:-NONE}"
ifconfig | awk '/^utun/{n=$1; sub(":","",n); m="?"; for(i=1;i<=NF;i++) if($i=="mtu") m=$(i+1); print n, "MTU", m}'
echo
echo "Multiple utuns (especially MTU 1380 with no IPv4) = possible zombies from"
echo "kill/respawn cycles. Real fix is a reboot."

# --- 4. Routing ---
banner "4. Default routes"
netstat -rn -f inet | grep -E "^default|^Destination"

banner "5. Where common endpoints route to right now"
for host in speedtest.net fast.com speed.cloudflare.com 1.1.1.1; do
  echo "  $host:"
  route -n get "$host" 2>/dev/null | grep -E "  interface:|  gateway:" | sed 's/^/    /'
done

# --- 6. Latency probes ---
banner "6. Latency probes (gateway, public DNS, internet)"
GW=$(route -n get default 2>/dev/null | awk '/gateway:/{print $2}')
echo "Gateway: $GW"
for tgt in "$GW" 1.1.1.1 8.8.8.8 104.16.124.96; do
  echo "--- ping $tgt ---"
  ping -c 5 -i 0.5 -W 1000 "$tgt" 2>&1 | tail -3
done

# --- 7. DNS resolution timing ---
banner "7. DNS resolution timing"
for h in speed.cloudflare.com www.google.com apple.com; do
  echo "--- $h ---"
  dig +tries=1 +time=2 "$h" 2>&1 | grep -E "Query time|ANSWER SECTION" -A1
done

# --- 8. Parallel tcpdump: wifi vs tunnel during a download ---
banner "8. Parallel capture: wifi + tunnel during a Cloudflare download"
echo "10-second download from Cloudflare; capturing TCP on both interfaces."
echo
echo "  TCP packets on $VPN_UTUN    -> traffic IS being tunnelled"
echo "  TCP on en0 but throughput bad -> wifi/host stack issue"
echo "  Neither sees packets         -> DNS or connect() is failing"
echo

EN0_CAP=$(mktemp)
VPN_CAP=$(mktemp)
CURL_OUT=$(mktemp)

# shellcheck disable=SC2024
# The redirect runs as the calling user, but mktemp created these files
# owned by that user — sudo'd tcpdump inherits the open fd. Works fine.
sudo tcpdump -i en0 -n -c 50 'tcp port 443' > "$EN0_CAP" 2>&1 &
EN0_PID=$!
if [ -n "$VPN_UTUN" ]; then
  # shellcheck disable=SC2024
  sudo tcpdump -i "$VPN_UTUN" -n -c 50 'tcp' > "$VPN_CAP" 2>&1 &
  VPN_PID=$!
fi

curl -s -o /dev/null --max-time 10 \
  -w "  curl: %{size_download} bytes in %{time_total}s — %{speed_download} bytes/sec\n" \
  "https://speed.cloudflare.com/__down?bytes=104857600" > "$CURL_OUT" 2>&1

sleep 2
sudo kill "$EN0_PID" 2>/dev/null
[ -n "${VPN_PID:-}" ] && sudo kill "$VPN_PID" 2>/dev/null
wait 2>/dev/null

echo "--- curl result ---"
cat "$CURL_OUT"
echo
echo "--- packets on en0 (wifi) ---"
echo "  TCP packets seen: $(grep -c 'IP ' "$EN0_CAP" 2>/dev/null || echo 0)"
head -5 "$EN0_CAP" 2>/dev/null
echo
if [ -n "$VPN_UTUN" ]; then
  echo "--- packets on $VPN_UTUN (tunnel) ---"
  echo "  TCP packets seen: $(grep -c 'IP ' "$VPN_CAP" 2>/dev/null || echo 0)"
  head -5 "$VPN_CAP" 2>/dev/null
fi
rm -f "$EN0_CAP" "$VPN_CAP" "$CURL_OUT"

# --- 9. Traceroute ---
banner "9. Traceroute to Cloudflare (find where packets die)"
traceroute -n -w 2 -q 1 -m 12 1.1.1.1 2>&1 | head -15

banner "Done"
echo "Output saved to: $OUT"
echo "Drag that file into Slack / share with whoever's helping you."
