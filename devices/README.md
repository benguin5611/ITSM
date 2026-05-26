# devices

Docs and tooling for the device fleet — workstations, MDM, and anything that runs on a developer's machine.

## Contents

### [macos-storage-cleanup.md](macos-storage-cleanup.md)

A practical guide to diagnosing high disk usage on macOS and reclaiming space safely. Aimed at developer workstations on APFS. Covers:

- Where space actually goes on a modern Mac (APFS volume structure, snapshots, "Other" storage).
- A priority order for what to clean first — biggest wins, lowest risk.
- Developer-specific stores that quietly grow into tens or hundreds of GB: language toolchain caches, build artefacts, package manager stores, IDE caches.
- Application caches and what's safe to delete.

### [macos-network-diag/](macos-network-diag/)

User-facing diagnostics for "the internet feels slow on my Mac". Run before toggling wifi or rebooting — those actions destroy the state needed to diagnose. Contains:

- A ~5 second wifi radio check (`wdutil`, SSID, `networkQuality`).
- A ~90 second comprehensive diagnostic that captures wifi state, VPN tunnel detection, routing, per-hop latency, DNS timing, parallel `tcpdump` on `en0` and the VPN utun during a controlled download, and traceroute.
- A reading guide mapping signals to likely root causes (wifi radio, ISP, VPN, DNS, host TCP stack).

See [macos-network-diag/README.md](macos-network-diag/README.md).

### [sbom/](sbom/)

Automated monthly SBOM collection from macOS developer machines in SPDX 2.3 format. A bash script on each device scans Nix and Homebrew packages, the result is uploaded via a presigned URL to S3, and a Lambda validates the SPDX schema before long-term storage. Contains:

- The on-device collection script.
- The Go Lambda that issues presigned URLs and validates uploads.
- Terraform for the S3 bucket, Lambda, IAM, KMS, logs, alarms, and secrets.
- The SPDX 2.3 JSON schema used for validation.

See [sbom/README.md](sbom/README.md) for deployment, operations, and the full architecture.

### [twingate-mdm/](twingate-mdm/)

MDM audit + remediation scripts for Twingate on macOS. Enforces Twingate runs at login via a locked-down LaunchAgent, and mitigates the zombie utun adapter bug caused by killing Twingate's userspace before its network extension can release the tunnel. Contains:

- `twingate-audit.sh` — compliance check (exit `0` = compliant, `1` = remediate) for MDM compliance loops.
- `twingate-remediate.sh` — installs the LaunchAgent, `chflags uchg`s it, and cleans up zombie utuns. `--no-zombie-mitigation` flag skips the utun step.
- Diagnostic bypass via `/var/db/.twingate-diag-bypass` so IT can pause enforcement during triage without touching MDM policy.

See [twingate-mdm/README.md](twingate-mdm/README.md) for the `KeepAlive` design, MDM deployment notes, and known limits.

## Conventions

- One topic per subfolder. Single-page guides can live as top-level `.md` files; promote to a folder once there's more than one artefact (scripts, infra, schemas) to ship alongside.
- Each subfolder has its own `README.md` covering what it is, how to use it, and update cadence.
- Infra-as-code (Terraform, Lambda, etc.) lives next to the docs that describe it.
