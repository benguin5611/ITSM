# devices

Docs and tooling for the device fleet — workstations, MDM, and anything that runs on a developer's machine.

## Contents

- [storage.md](storage.md) — diagnosing and cleaning up disk usage on macOS developer machines.
- [sbom/](sbom/) — automated SBOM collection (SPDX 2.3) for installed packages across the fleet.

## Conventions

- One topic per subfolder. Keep top-level files for single-page guides; promote to a folder once there's more than one artefact (scripts, infra, schemas) to ship alongside.
- Each subfolder has its own `README.md` covering what it is, how to use it, and update cadence.
- Infra-as-code (Terraform, Lambda, etc.) lives next to the docs that describe it.
