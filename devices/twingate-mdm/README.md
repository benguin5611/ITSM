# twingate-mdm

MDM audit + remediation scripts for Twingate on macOS.

Solves two problems:

1. **Enforce Twingate runs at login.** Standard MDM territory — `RunAtLoad` LaunchAgent + immutable plist.
2. **Fix the zombie utun bug.** Twingate's macOS client leaves orphaned utun adapters behind when its userspace process is killed before the network extension can release the tunnel. These zombies sit in the kernel routing table and black-hole packets, causing throughput collapse. The previous version of this enforcement script *caused* the bug by using `KeepAlive: true` — respawning Twingate before it could clean up.

## Scripts

### `twingate-audit.sh`
Compliance check. Exit `0` = compliant, exit `1` = needs remediation. Designed to be polled by MDM compliance loops.

### `twingate-remediate.sh`
Installs the LaunchAgent, locks it with `chflags uchg`, and mitigates zombie utun adapters.

Flags:
- `--no-zombie-mitigation` — skip the utun cleanup step.

## Why `KeepAlive` is a dict, not `true`

```xml
<key>KeepAlive</key>
<dict>
    <key>Crashed</key>
    <true/>
    <key>SuccessfulExit</key>
    <false/>
</dict>
```

Respawns Twingate on crash or non-zero exit, but lets a clean Quit succeed. The clean exit path gives the network extension time to release its utun adapter. Unconditional `KeepAlive: true` causes the kernel to retain the utun while userspace is respawned with a new one, accumulating zombies over time.

## Diagnostic bypass

```sh
sudo touch /var/db/.twingate-diag-bypass
```

Both scripts no-op for 10 minutes. Lets IT pause enforcement during triage without modifying MDM policy.

## MDM deployment

Designed to plug into any MDM that supports a compliance check + remediation pattern: Jamf (Extension Attribute + Smart Group policy), Kandji (Custom App or Library Item), Intune (Custom Compliance), Workspace ONE, Mosyle. Key requirements:

- Run as root
- Run on a schedule (every 15–60 min) or login + recurring check
- Pair `twingate-audit.sh` and `twingate-remediate.sh` via your MDM's compliance/remediation model

## Limits

- Zombie utun adapters still exist in kernel space after mitigation. Only a reboot truly clears them.
- Zombie detection only matches utuns with MTU 1380 (Twingate's documented default) and no IPv4. MTU 1500 zombies aren't auto-mitigated — too many other macOS services use that MTU (iCloud Private Relay, generic VPNs). Reboot clears them for free.
- No uninstaller. Remove with `sudo chflags nouchg /Library/LaunchAgents/com.twingate.macos.plist && sudo rm /Library/LaunchAgents/com.twingate.macos.plist && launchctl bootout gui/$(id -u)/com.twingate.macos`.

## Status

These scripts have been tested on the author's machine but are not battle-tested across the macOS version matrix. Treat as a reference implementation, not a finished product.
