#!/bin/zsh
#
# twingate-remediate.sh — Twingate LaunchAgent install + zombie utun mitigation
#
# Installs a LaunchAgent that:
#   - Auto-starts Twingate at login (RunAtLoad)
#   - Respawns Twingate ONLY on crash or non-zero exit (NOT on clean Quit).
#     Unconditional respawn causes the Twingate network extension to leave
#     zombie utun adapters behind, which black-hole packets and tank
#     throughput. Scoping KeepAlive to actual failure lets the user Quit
#     cleanly during triage while still enforcing presence at login.
#   - Throttles respawn to once per 30 seconds (avoid crash-loop thrash)
#   - Marks itself Interactive so launchd gives it appropriate scheduling
#
# Locks the plist with `chflags uchg` (user-immutable, removable with
# sudo) — stops casual tampering, doesn't require single-user mode to
# clear, doesn't break Twingate's own installer when it ships updates.
#
# After install, identifies likely zombie utun adapters (Twingate-shaped
# interfaces from prior kill/respawn cycles) and brings them admin-down
# with their routes stripped. The interfaces still exist in kernel space —
# only a reboot truly removes them — but they stop affecting routing
# decisions, which is what causes the throughput symptom.
#
# Flags:
#   --no-zombie-mitigation   Skip the zombie utun cleanup step.
#                            Set if other VPN clients on the same machine
#                            use Twingate-shaped utuns and you don't want
#                            those touched.
#
# Diagnostic bypass:
#   If /var/db/.twingate-diag-bypass exists and is < 10 minutes old, this
#   script no-ops. Lets IT pause enforcement during triage. Create with:
#     sudo touch /var/db/.twingate-diag-bypass
#

[[ $EUID -eq 0 ]] || { echo "must run as root"; exit 1; }

PLIST="/Library/LaunchAgents/com.twingate.macos.plist"
BYPASS="/var/db/.twingate-diag-bypass"
ZOMBIE_MITIGATION=1

# --- Flag parsing ---
for arg in "$@"; do
    case "$arg" in
        --no-zombie-mitigation) ZOMBIE_MITIGATION=0 ;;
    esac
done

# --- Diagnostic bypass ---
if [[ -f "$BYPASS" ]]; then
    BYPASS_MTIME=$(stat -f %m "$BYPASS")
    NOW=$(date +%s)
    AGE=$(( NOW - BYPASS_MTIME ))
    if (( AGE >= 0 && AGE < 600 )); then
        echo "Diagnostic bypass active (${AGE}s old, expires in $((600 - AGE))s) — skipping"
        exit 0
    else
        rm -f "$BYPASS"
    fi
fi

# --- Clear any previous immutable flags so we can rewrite ---
# `|| true` because the flag may not be set — but real errors (locked,
# SIP-protected, etc.) are surfaced rather than swallowed silently.
chflags nouchg "$PLIST" 2>&1 || true
chflags noschg "$PLIST" 2>&1 || true

cat > "$PLIST" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.twingate.macos</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/Twingate.app/Contents/MacOS/Twingate</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>Crashed</key>
        <true/>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>ThrottleInterval</key>
    <integer>30</integer>
    <key>ProcessType</key>
    <string>Interactive</string>
</dict>
</plist>
EOF

chown root:wheel "$PLIST"
chmod 644 "$PLIST"
chflags uchg "$PLIST"

# --- Bootstrap into the console user's session ---
# Errors are surfaced (no 2>/dev/null) so MDM logs catch failures.
# `bootout` may legitimately fail if the agent wasn't previously loaded —
# that's expected, the subsequent bootstrap is what matters.
# `kickstart` after bootstrap guarantees Twingate is actually running
# afterwards; RunAtLoad alone doesn't always stick on re-bootstrap.
CONSOLE_USER=$(stat -f%Su /dev/console)
if [[ -n "$CONSOLE_USER" && "$CONSOLE_USER" != "root" && "$CONSOLE_USER" != "loginwindow" ]]; then
    CONSOLE_UID=$(id -u "$CONSOLE_USER")
    launchctl bootout "gui/$CONSOLE_UID/com.twingate.macos" 2>&1 || true
    if ! launchctl bootstrap "gui/$CONSOLE_UID" "$PLIST"; then
        echo "ERROR: launchctl bootstrap failed"
        exit 1
    fi
    launchctl kickstart "gui/$CONSOLE_UID/com.twingate.macos" || \
        echo "WARNING: kickstart failed; Twingate may not be running"
fi

# --- Zombie utun mitigation ---
ZOMBIE_COUNT=0
if (( ZOMBIE_MITIGATION == 1 )); then
    ACTIVE_UTUN=$(ifconfig | awk '
      /^utun/ { name=$1; sub(":","",name) }
      /inet 100\./ { print name; exit }
    ')

    for iface in $(ifconfig -l | tr ' ' '\n' | grep '^utun'); do
        [[ "$iface" == "$ACTIVE_UTUN" ]] && continue

        # Skip if the interface has an IPv4 address — something else owns
        # it (any active VPN tunnel). Note: IPv6 link-local is NOT a
        # useful filter — every utun on macOS gets one by default.
        if ifconfig "$iface" 2>/dev/null | grep -qE "^[[:space:]]+inet [0-9]"; then
            continue
        fi

        MTU=$(ifconfig "$iface" 2>/dev/null | awk '/mtu/ {for(i=1;i<=NF;i++) if($i=="mtu") print $(i+1)}')

        # Only mitigate utuns with Twingate's documented default MTU (1380).
        # MTU 1500 is deliberately NOT matched: too many other things use
        # it (iCloud Private Relay, generic system VPNs), false-positive
        # risk outweighs catching the rarer 1500 zombies. Rebooting clears
        # the 1500 ones for free.
        if [[ "$MTU" == "1380" ]]; then
            echo "Mitigating likely zombie: $iface (MTU=$MTU)"
            netstat -rn -f inet | awk -v i="$iface" '$NF==i {print $1}' | \
                while read -r dest; do
                    route delete -ifp "$iface" "$dest" 2>/dev/null
                done
            ifconfig "$iface" down 2>/dev/null
            ZOMBIE_COUNT=$((ZOMBIE_COUNT + 1))
        fi
    done
fi

echo "Twingate LaunchAgent installed and loaded (mitigated $ZOMBIE_COUNT zombie utuns)"
exit 0
