# devices

Docs and tooling for the device fleet — workstations, MDM, and anything that runs on a developer's machine.

## Contents

### [macos-storage-cleanup.md](macos-storage-cleanup.md)

A practical guide to diagnosing high disk usage on macOS and reclaiming space safely. Aimed at developer workstations on APFS. Covers:

- Where space actually goes on a modern Mac (APFS volume structure, snapshots, "Other" storage).
- A priority order for what to clean first — biggest wins, lowest risk.
- Developer-specific stores that quietly grow into tens or hundreds of GB: language toolchain caches, build artefacts, package manager stores, IDE caches.
- Application caches and what's safe to delete.

### [sbom/](sbom/)

Automated monthly SBOM collection from macOS developer machines in SPDX 2.3 format. A bash script on each device scans Nix and Homebrew packages, the result is uploaded via a presigned URL to S3, and a Lambda validates the SPDX schema before long-term storage. Contains:

- The on-device collection script.
- The Go Lambda that issues presigned URLs and validates uploads.
- Terraform for the S3 bucket, Lambda, IAM, KMS, logs, alarms, and secrets.
- The SPDX 2.3 JSON schema used for validation.

See [sbom/README.md](sbom/README.md) for deployment, operations, and the full architecture.

## Conventions

- One topic per subfolder. Single-page guides can live as top-level `.md` files; promote to a folder once there's more than one artefact (scripts, infra, schemas) to ship alongside.
- Each subfolder has its own `README.md` covering what it is, how to use it, and update cadence.
- Infra-as-code (Terraform, Lambda, etc.) lives next to the docs that describe it.
