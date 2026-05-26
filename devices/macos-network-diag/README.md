# macos-network-diag

User-facing diagnostics for "the internet feels slow on my Mac". Run these *before* toggling wifi or rebooting — those actions destroy the state we need to diagnose.

## Scripts

### `wifi.sh`
Quick wifi radio check. ~5 seconds. Captures `wdutil info`, current SSID, and a `networkQuality` sample. Use this first if you suspect wifi.

```sh
bash wifi.sh
```

### `slow.sh`
Comprehensive network diagnostic. ~90 seconds. Captures:

- Wifi radio state
- Active VPN tunnel detection (any utun with a 100.x.x.x address)
- Routing snapshot + where common endpoints route to
- Latency probes at each hop (gateway, public DNS, internet)
- DNS resolution timing
- **Parallel `tcpdump` on wifi (`en0`) and the VPN tunnel** during a controlled Cloudflare download — the "is it the tunnel or the host" decider
- Traceroute to `1.1.1.1`

Output is timestamped and saved to `~/Downloads/slow-diag-*.log`.

```sh
bash slow.sh
```

## Reading the output

| Signal | Conclusion |
|---|---|
| `wdutil` shows 2.4 GHz / weak RSSI / low Tx rate | Wifi radio is the bottleneck |
| Gateway ping bad, public pings also bad | Wifi or LAN |
| Gateway ping fine, public pings bad | ISP or upstream |
| TCP packets on the VPN utun during the curl | Traffic is being tunnelled |
| TCP on en0 but throughput bad, wifi state fine | Host TCP stack |
| DNS query time > 500 ms | Resolver problem |
| Traceroute dies at hop 2–3 | ISP edge |
