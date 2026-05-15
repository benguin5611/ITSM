#!/bin/bash
#
# sbom-audit-simple — on-command macOS SBOM generator (SPDX 2.3)
#
# A stripped-down alternative to sbom-audit-spdx for users who don't need
# Nix scanning, monthly throttling, or Lambda upload. Runs Syft once,
# writes a cleaned SPDX 2.3 JSON file to disk, and exits.
#
# Usage:
#   sbom-audit-simple                           # scan / (full system)
#   sbom-audit-simple --output /path/to.json    # custom output path
#   sbom-audit-simple --fast                    # scan Homebrew Cellar only (~2 min)
#   sbom-audit-simple --monthly                 # MDM-scheduled: skip if already run this month
#   sbom-audit-simple --delay 3600              # MDM-scheduled: random sleep 0..N seconds before scan
#   sbom-audit-simple --force                   # bypass --monthly throttle
#   sbom-audit-simple --help
#
# Run modes:
#   - Locally:     ./sbom-audit-simple.sh
#   - MDM script:  deploy as a custom script (no env vars required). For a daily-scheduled
#                  deployment, add --monthly --delay 3600 so each device runs once per month
#                  and uploads are spread across an hour.
#   - MDM self-service: expose as an on-demand action for the user (no flags needed).
#
# Requirements: macOS, Homebrew (auto-installs syft and jq if missing).

set -euo pipefail

OUTPUT=""
SCAN_PATH="/"
FAST=0
MONTHLY=0
FORCE=0
DELAY=0
STATE_DIR="${HOME}/.sbom-audit-simple"

print_help() {
	cat <<'EOF'
sbom-audit-simple — generate an SPDX 2.3 SBOM for this Mac.

USAGE:
  sbom-audit-simple [--output PATH] [--fast] [--monthly] [--delay SECS] [--force]
  sbom-audit-simple --help

OPTIONS:
  --output PATH   Where to write the SBOM. Default: ~/Downloads/sbom-<hostname>-<timestamp>.spdx.json
  --fast          Scan only /opt/homebrew/Cellar (or /usr/local/Cellar). Faster, fewer packages.
  --monthly       Skip if already run this calendar month. Marker: ~/.sbom-audit-simple/.last-run-YYYY-MM.
                  Intended for daily-scheduled MDM deployments — pair with --delay.
  --delay SECS    Sleep a random 0..SECS seconds before scanning. Use to spread fleet-wide load
                  when scheduled by MDM (e.g. --delay 3600 for a one-hour spread).
  --force         Bypass --monthly throttle. No effect without --monthly.
  --help, -h      Show this help.

OUTPUT:
  Two files are written side-by-side:
    1. An SPDX 2.3 JSON file (with CPE externalRefs removed and filesAnalyzed: false
       on every package — the format accepted by https://tools.spdx.org/app/convert/).
    2. A flat CSV companion at the same path with .csv extension, columns:
       name, version, license, supplier, downloadLocation, purl.
  The CSV is for spreadsheet/BI use; the JSON is the authoritative SBOM.
EOF
}

while [ $# -gt 0 ]; do
	case "$1" in
	--output)
		[ $# -ge 2 ] || { echo "✗ --output requires a path" >&2; exit 1; }
		OUTPUT="$2"
		shift 2
		;;
	--fast)
		FAST=1
		shift
		;;
	--monthly)
		MONTHLY=1
		shift
		;;
	--delay)
		[ $# -ge 2 ] || { echo "✗ --delay requires a number of seconds" >&2; exit 1; }
		[[ "$2" =~ ^[0-9]+$ ]] || { echo "✗ --delay must be a non-negative integer" >&2; exit 1; }
		DELAY="$2"
		shift 2
		;;
	--force)
		FORCE=1
		shift
		;;
	--help | -h)
		print_help
		exit 0
		;;
	*)
		# %q shell-quotes $1, neutralising any terminal escape sequences a
		# caller might inject via argv.
		printf '✗ Unknown argument: %q\n' "$1" >&2
		print_help >&2
		exit 1
		;;
	esac
done

# --- monthly throttle (opt-in) --------------------------------------------------

if [ "$MONTHLY" -eq 1 ]; then
	mkdir -p "$STATE_DIR"
	MARKER="${STATE_DIR}/.last-run-$(date -u +%Y-%m)"
	if [ -f "$MARKER" ] && [ "$FORCE" -ne 1 ]; then
		echo "✓ Already ran this month ($(basename "$MARKER")). Use --force to override."
		exit 0
	fi
fi

# --- random delay (opt-in) ------------------------------------------------------

if [ "$DELAY" -gt 0 ]; then
	# $RANDOM is 0..32767; scale to 0..DELAY
	SLEEP_FOR=$(( RANDOM * DELAY / 32767 ))
	echo "→ Sleeping ${SLEEP_FOR}s (random 0..${DELAY}) to spread fleet load..."
	sleep "$SLEEP_FOR"
fi

# --- dependency check / install -------------------------------------------------
#
# ACCEPTED RISKS (documented for auditors):
#
#  1. Homebrew is auto-installed via the upstream `curl | bash` installer if
#     missing. This executes unsigned remote code from raw.githubusercontent.com.
#     We accept this because: (a) it is the upstream-blessed install method,
#     (b) the audience for this simple script is local users and MDM self-service
#     flows where "it just works" matters more than supply-chain rigour, and
#     (c) tighter pipelines should use sbom-audit-spdx.sh and provision Homebrew
#     out-of-band via signed MDM packaging.
#
#  2. `brew install syft` / `brew install jq` are unpinned. Pinning would
#     require maintaining a known-good version table and breaks transparently
#     when Homebrew rotates formulae. Same audience trade-off as above —
#     convenience outweighs marginal exposure for solo/self-service use; for
#     tighter pipelines, use sbom-audit-spdx.sh with pre-provisioned tooling.

ensure_homebrew() {
	if command -v brew &>/dev/null; then
		return 0
	fi
	# Brew may exist but not be on PATH (common in non-interactive shells like
	# MDM script runners). Probe the two standard locations directly before
	# falling back to the upstream installer.
	if [ -x /opt/homebrew/bin/brew ]; then
		export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:${PATH}"
		return 0
	fi
	if [ -x /usr/local/bin/brew ]; then
		export PATH="/usr/local/bin:/usr/local/sbin:${PATH}"
		return 0
	fi
	echo "→ Homebrew not found. Installing via upstream installer (accepted risk — see header comment)..."
	if ! /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
		echo "✗ Homebrew install failed" >&2
		return 1
	fi
	# Don't `eval "$(brew shellenv)"` — it executes arbitrary brew output as
	# shell. Setting PATH explicitly is all this script needs.
	if [ -x /opt/homebrew/bin/brew ]; then
		export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:${PATH}"
	elif [ -x /usr/local/bin/brew ]; then
		export PATH="/usr/local/bin:/usr/local/sbin:${PATH}"
	fi
}

ensure_tool() {
	local tool="$1"
	if command -v "$tool" &>/dev/null; then
		return 0
	fi
	echo "→ Installing $tool via Homebrew (unpinned — accepted risk, see header comment)..."
	brew install "$tool"
}

ensure_homebrew
ensure_tool jq
ensure_tool syft

# --- scan paths -----------------------------------------------------------------

if [ "$FAST" -eq 1 ]; then
	if [ -d /opt/homebrew/Cellar ]; then
		SCAN_PATH="/opt/homebrew/Cellar"
	elif [ -d /usr/local/Cellar ]; then
		SCAN_PATH="/usr/local/Cellar"
	else
		echo "✗ --fast mode requires Homebrew Cellar; not found" >&2
		exit 1
	fi
fi

HOSTNAME_SAFE=$(hostname -s | tr -c 'A-Za-z0-9._-' '-')
TIMESTAMP=$(date -u +%Y-%m-%dT%H-%M-%SZ)

if [ -z "$OUTPUT" ]; then
	# Default to ~/Downloads for convenience — it's the path most users will
	# look in first, and Finder will surface the file immediately. Override
	# with --output if you want it somewhere else (e.g. a shared drop folder
	# your MDM collects from, /tmp for throwaway runs, etc.).
	OUTPUT="${HOME}/Downloads/sbom-${HOSTNAME_SAFE}-${TIMESTAMP}.spdx.json"
	mkdir -p "${HOME}/Downloads"
fi

# Refuse to follow a pre-existing symlink at $OUTPUT. Defends against a
# symlink-swap attack where a non-privileged user pre-creates $OUTPUT as a
# symlink to a sensitive file (e.g. /etc/sudoers) and the script — when run
# under MDM as root — overwrites the target. -L tests for symlink even when
# the link target is missing.
if [ -L "$OUTPUT" ]; then
	echo "✗ Refusing to write: $OUTPUT is a symlink" >&2
	exit 1
fi

# --- run syft -------------------------------------------------------------------

# Create a private temp directory (mktemp -d uses O_CREAT|O_EXCL and 0700 perms)
# and place the raw SBOM inside it. This eliminates any symlink-attack window
# on the raw path: only this process (and root) can write into the directory.
# macOS mktemp doesn't substitute X's mid-string, so we can't get an atomic
# .json-suffixed file directly — the dir-then-fixed-name pattern is the
# portable equivalent.
RAW_DIR=$(mktemp -d -t sbom-simple-raw)
RAW="${RAW_DIR}/raw.json"
trap 'rm -rf "$RAW_DIR"' EXIT

echo "→ Scanning $SCAN_PATH with syft..."
echo "  (this can take several minutes for a full system scan)"

# Excludes fall into three groups:
#   1. Source-control internals — .git contains pack files that syft mis-detects
#      as packages and scanning them balloons runtime with no real signal.
#   2. Per-language package-manager caches — these are downloaded copies of
#      registry artifacts, not installed packages. The authoritative inventory
#      lives in each project's lock file (which CI/GitHub SBOM already captures);
#      scanning the caches duplicates that data and inflates the SBOM with
#      transitive dependencies that aren't actually installed on the device.
#   3. macOS system & app-container paths — /System and /private/* are SIP/TCC
#      protected (mostly unreadable, no installed packages live there), and the
#      Library/* paths hold app caches and sandboxed app data, not system
#      packages. Including them produces permission-denied noise and slows the
#      scan dramatically.
#   4. macOS system binaries — /usr/sbin, /usr/libexec, /usr/bin, /sbin are
#      Apple-supplied binaries (not third-party packages) and frequently host
#      EDR/AV tooling (CrowdStrike, Bitdefender, etc.) under restricted-stat
#      subdirectories. Without excluding these, a single lstat-denied path
#      under e.g. /usr/sbin/authserver aborts the entire scan — Syft treats
#      stat failures inside the scan root as fatal, not warnings.
# Resource safeguards:
#   * `taskpolicy -b` runs syft under macOS background QoS, throttling CPU and
#     yielding to interactive work — the user keeps their machine responsive
#     while the scan runs (matters because a full / scan can take 5-10 min).
#   * A 1-hour watchdog kills syft if it hangs (e.g. a filesystem that never
#     returns from stat). Without this, set -e wouldn't help because syft would
#     just spin forever; the watchdog guarantees the script terminates.
SYFT_TIMEOUT=3600

SYFT_CHECK_FOR_APP_UPDATE=false taskpolicy -b syft scan "dir:$SCAN_PATH" \
	-o spdx-json="$RAW" \
	-q \
	--exclude '**/.git/**' \
	--exclude '**/node_modules/**' \
	--exclude '**/.npm/**' \
	--exclude '**/.yarn/**' \
	--exclude '**/.pnpm-store/**' \
	--exclude '**/.cargo/registry/**' \
	--exclude '**/.m2/**' \
	--exclude '**/.gradle/**' \
	--exclude '**/.nuget/**' \
	--exclude '**/.cocoapods/**' \
	--exclude '**/.bundle/**' \
	--exclude '**/go/pkg/mod/**' \
	--exclude '**/Library/Caches/**' \
	--exclude '**/Library/Containers/**' \
	--exclude '**/Library/Application Support/**' \
	--exclude './System/**' \
	--exclude './private/var/**' \
	--exclude './private/etc/**' \
	--exclude './private/tmp/**' \
	--exclude './usr/sbin/**' \
	--exclude './usr/libexec/**' \
	--exclude './usr/bin/**' \
	--exclude './sbin/**' &
SYFT_PID=$!

# Watchdog: kill syft if it runs past SYFT_TIMEOUT seconds. The watchdog
# itself is killed in the cleanup line below once syft finishes naturally.
(sleep "$SYFT_TIMEOUT" && kill "$SYFT_PID" 2>/dev/null) &
WATCHDOG_PID=$!

# Wait for syft, capturing its exit code. `set -e` is temporarily relaxed
# around `wait` because we want to handle non-zero exits ourselves below.
set +e
wait "$SYFT_PID"
SYFT_EXIT=$?
set -e
kill "$WATCHDOG_PID" 2>/dev/null || true
wait "$WATCHDOG_PID" 2>/dev/null || true

if [ "$SYFT_EXIT" -ne 0 ]; then
	if [ "$SYFT_EXIT" -gt 128 ]; then
		echo "✗ syft was killed by signal $((SYFT_EXIT - 128)) — likely the ${SYFT_TIMEOUT}s watchdog timeout" >&2
	else
		echo "✗ syft exited non-zero (status $SYFT_EXIT)" >&2
	fi
	exit 1
fi

if [ ! -s "$RAW" ]; then
	echo "✗ syft produced no output" >&2
	exit 1
fi

# --- normalise: enforce SPDX 2.3, strip CPE refs, set filesAnalyzed: false ------

echo "→ Normalising SPDX output..."

NAMESPACE_UUID=$(uuidgen 2>/dev/null || od -An -N16 -tx1 /dev/urandom | tr -d ' \n')

# Write to a sibling temp file and rename atomically. If jq fails midway (OOM,
# disk full, malformed input), the rename never happens and $OUTPUT keeps its
# previous contents (or stays absent) — no truncated/partial SBOM is ever
# observable to a downstream consumer polling the directory.
#
# Use mktemp rather than "${OUTPUT}.tmp.$$": mktemp creates the file atomically
# with O_CREAT|O_EXCL, so an attacker who can write to dirname "$OUTPUT" can't
# pre-place a symlink at the temp path to redirect the jq write.
OUTPUT_TMP=$(mktemp "${OUTPUT}.tmp.XXXXXX")
trap 'rm -rf "$RAW_DIR"; rm -f "$OUTPUT_TMP"' EXIT

jq --arg ns "http://spdx.org/spdxdocs/${HOSTNAME_SAFE}-${NAMESPACE_UUID}" '
	.spdxVersion = "SPDX-2.3"
	| .documentNamespace = $ns
	| .packages = (
		(.packages // []) | map(
			.filesAnalyzed = false
			| del(.licenseInfoFromFiles, .packageVerificationCode, .hasFiles)
			| if .versionInfo == "" then del(.versionInfo) else . end
			| if .externalRefs then .externalRefs |= map(select(.referenceType != "cpe23Type")) else . end
			| if .externalRefs == [] then del(.externalRefs) else . end
		)
	)
' "$RAW" >"$OUTPUT_TMP"

if [ ! -s "$OUTPUT_TMP" ]; then
	echo "✗ jq normalisation produced empty output" >&2
	exit 1
fi

mv "$OUTPUT_TMP" "$OUTPUT"

# --- CSV companion --------------------------------------------------------------
#
# Produce a flat CSV alongside the JSON for spreadsheet/BI tooling. We use jq's
# built-in @csv filter, which handles quoting and embedded commas/quotes per
# RFC 4180. The purl column is extracted from externalRefs (the package URL is
# the most analyst-useful identifier — it encodes ecosystem, name, and version
# in a single string).
#
# CSV path mirrors the JSON path with the extension swapped:
#   foo.spdx.json → foo.csv
#   foo.json      → foo.csv
#   foo           → foo.csv

case "$OUTPUT" in
	*.spdx.json) CSV_OUTPUT="${OUTPUT%.spdx.json}.csv" ;;
	*.json)      CSV_OUTPUT="${OUTPUT%.json}.csv" ;;
	*)           CSV_OUTPUT="${OUTPUT}.csv" ;;
esac

if [ -L "$CSV_OUTPUT" ]; then
	echo "✗ Refusing to write: $CSV_OUTPUT is a symlink" >&2
	exit 1
fi

echo "→ Writing CSV companion..."

CSV_TMP=$(mktemp "${CSV_OUTPUT}.tmp.XXXXXX")
# Update the trap so the CSV temp file is cleaned up on any failure too.
trap 'rm -rf "$RAW_DIR"; rm -f "$OUTPUT_TMP" "$CSV_TMP"' EXIT

{
	echo '"name","version","license","supplier","downloadLocation","purl"'
	# Defuse CSV formula injection (CWE-1236): SPDX field values originate from
	# untrusted third-party package metadata. If any starts with =, +, -, @,
	# tab, or CR, Excel/Sheets/Calc will execute it as a formula when the
	# analyst opens the file. Prefix such values with a single apostrophe,
	# Excel's literal-text marker — invisible in normal display, disarms the
	# formula. jq's @csv handles RFC 4180 quoting on top.
	jq -r '
		def safe: tostring | if test("^[=+\\-@\t\r]") then "\u0027" + . else . end;
		.packages[] | [
			(.name // "" | safe),
			(.versionInfo // "" | safe),
			((.licenseConcluded // .licenseDeclared // "") | safe),
			(.supplier // "" | safe),
			(.downloadLocation // "" | safe),
			(((.externalRefs // []) | map(select(.referenceType == "purl") | .referenceLocator)[0] // "") | safe)
		] | @csv
	' "$OUTPUT"
} >"$CSV_TMP"

if [ ! -s "$CSV_TMP" ]; then
	echo "✗ CSV generation produced empty output" >&2
	exit 1
fi

mv "$CSV_TMP" "$CSV_OUTPUT"

# --- summary --------------------------------------------------------------------

PKG_COUNT=$(jq '.packages | length' "$OUTPUT")
SIZE=$(du -h "$OUTPUT" | awk '{print $1}')
CSV_SIZE=$(du -h "$CSV_OUTPUT" | awk '{print $1}')

if [ "$MONTHLY" -eq 1 ]; then
	: >"$MARKER" || echo "⚠ Could not write marker $MARKER (next scheduled run will re-execute)" >&2
fi

echo ""
echo "✓ SBOM written"
echo "  JSON:     $OUTPUT ($SIZE)"
echo "  CSV:      $CSV_OUTPUT ($CSV_SIZE)"
echo "  Packages: $PKG_COUNT"
echo "  Format:   SPDX 2.3 JSON + flat CSV"
