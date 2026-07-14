#!/bin/zsh
#
# twingate-audit.sh — Twingate LaunchAgent compliance check
#
# Reports compliant (exit 0) or non-compliant (exit 1). Intended to be run
# by an MDM compliance loop (Jamf Smart Group, Kandji Custom App, Intune
# Custom Compliance, etc.) paired with `twingate-remediate.sh`.
#
# Non-compliant conditions:
#   - LaunchAgent plist missing
#   - RunAtLoad missing or false
#   - ProgramArguments missing or wrong path
#   - KeepAlive not scoped correctly (must be a dict with Crashed=true,
#     not unconditional true — see twingate-remediate.sh for rationale)
#   - Unmitigated zombie utun present: up, no IPv4 address, MTU 1380
#     (adapters left behind by Twingate's kill/respawn behaviour;
#     twingate-remediate.sh brings them admin-down, a reboot removes them)
#
# Diagnostic bypass:
#   If /var/db/.twingate-diag-bypass exists and is < 10 minutes old, this
#   script reports compliant unconditionally. Lets IT pause enforcement
#   during triage without modifying MDM policy. Create with:
#     sudo touch /var/db/.twingate-diag-bypass
#

PLIST="/Library/LaunchAgents/com.twingate.macos.plist"
BYPASS="/var/db/.twingate-diag-bypass"

# --- Diagnostic bypass ---
if [[ -f "$BYPASS" ]]; then
    BYPASS_MTIME=$(stat -f %m "$BYPASS")
    NOW=$(date +%s)
    AGE=$(( NOW - BYPASS_MTIME ))
    if (( AGE >= 0 && AGE < 600 )); then
        echo "Diagnostic bypass active (${AGE}s old) — reporting compliant"
        exit 0
    fi
fi

# --- Plist presence and structure ---
if [[ ! -f "$PLIST" ]]; then
    echo "Twingate LaunchAgent missing"
    exit 1
fi

if ! /usr/libexec/PlistBuddy -c "Print :RunAtLoad" "$PLIST" 2>/dev/null | grep -q true; then
    echo "LaunchAgent malformed: RunAtLoad missing or false"
    exit 1
fi

if ! /usr/libexec/PlistBuddy -c "Print :ProgramArguments:0" "$PLIST" 2>/dev/null | grep -q "Twingate.app"; then
    echo "LaunchAgent malformed: ProgramArguments missing or wrong"
    exit 1
fi

# KeepAlive must be a dict with Crashed=true (not unconditional true).
# Unconditional respawn causes zombie utun accumulation.
if ! /usr/libexec/PlistBuddy -c "Print :KeepAlive:Crashed" "$PLIST" 2>/dev/null | grep -q true; then
    echo "LaunchAgent malformed: KeepAlive not scoped correctly"
    exit 1
fi

# --- Zombie utun check ---
# Detects the same population twingate-remediate.sh mitigates: utuns that
# are still up with no IPv4 address and Twingate's observed default MTU of
# 1380. The active tunnel (and any other live VPN, e.g. Tailscale) has an
# IPv4 address so it never matches, and adapters remediation has already
# brought admin-down are no longer up, so a remediated machine reports
# compliant. Only a reboot removes zombies from the kernel entirely.
ZOMBIE_UTUNS=0
for iface in $(ifconfig -lu | tr ' ' '\n' | grep '^utun'); do
    if ifconfig "$iface" 2>/dev/null | grep -qE "^[[:space:]]+inet [0-9]"; then
        continue
    fi
    MTU=$(ifconfig "$iface" 2>/dev/null | awk '/mtu/ {for(i=1;i<=NF;i++) if($i=="mtu") print $(i+1)}')
    if [[ "$MTU" == "1380" ]]; then
        ZOMBIE_UTUNS=$((ZOMBIE_UTUNS + 1))
    fi
done
if [[ "$ZOMBIE_UTUNS" -gt 0 ]]; then
    echo "Zombie utun adapters detected ($ZOMBIE_UTUNS unmitigated) — remediation or reboot required"
    exit 1
fi

echo "Twingate LaunchAgent in place"
exit 0
