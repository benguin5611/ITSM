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
#   - More than one Twingate-shaped utun present (zombie adapters from
#     Twingate's kill/respawn behaviour; only a reboot fully clears them)
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
# More than one 100.x interface = accumulated zombies. Only a reboot
# fully clears them; twingate-remediate.sh can mitigate routing impact.
TWINGATE_UTUNS=$(ifconfig | awk '/^utun/{name=$1; sub(":","",name)} /inet 100\./{print name}' | wc -l | tr -d ' ')
if [[ "$TWINGATE_UTUNS" -gt 1 ]]; then
    echo "Zombie utun adapters detected ($TWINGATE_UTUNS active) — reboot required"
    exit 1
fi

echo "Twingate LaunchAgent in place"
exit 0
