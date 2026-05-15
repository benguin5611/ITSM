#!/bin/bash
# SBOM Audit - Keychain Secret Provisioning (EXAMPLE)
#
# Optional alternative to distributing secrets as MDM custom-script env vars.
# Deploy as a separate MDM Custom Script (one-time run, runs as root). Stores
# SBOM secrets in the System Keychain so they are never exposed in the main
# script body, in script env vars, or in MDM logs.
#
# BEFORE DEPLOYING:
#   1. Replace every REPLACE_ME placeholder below with your real secrets.
#      Fetch them from Secrets Manager:
#        aws secretsmanager get-secret-value \
#          --secret-id device-sbom-audit/auth-token --query SecretString --output text
#        aws secretsmanager get-secret-value \
#          --secret-id device-sbom-audit/presign-secret --query SecretString --output text
#   2. Paste the edited script into your MDM's Custom Script library.
#      DO NOT commit the edited copy to git.
#   3. Set execution frequency to "Run once per device".
#
# AFTER DEPLOYING, verify on a target device with:
#   security find-generic-password -a "sbom-audit" -s "SBOM_LAMBDA_URL" \
#     -w /Library/Keychains/System.keychain

set -euo pipefail

KEYCHAIN="/Library/Keychains/System.keychain"
ACCOUNT="sbom-audit"

# === Set your secrets here (replace placeholders before deploying) ===
SBOM_LAMBDA_URL='https://REPLACE_ME.lambda-url.REGION.on.aws/'
SBOM_AUTH_TOKEN='REPLACE_ME_WITH_BEARER_TOKEN'
SBOM_PRESIGN_SECRET='REPLACE_ME_WITH_PRESIGN_SECRET'
# =====================================================================

store_secret() {
    local service="$1"
    local value="$2"

    # Remove existing entry if present (prevents duplicate errors on re-run)
    security delete-generic-password \
        -a "$ACCOUNT" \
        -s "$service" \
        "$KEYCHAIN" 2>/dev/null || true

    security add-generic-password \
        -a "$ACCOUNT" \
        -s "$service" \
        -w "$value" \
        "$KEYCHAIN"

    echo "Stored $service in keychain"
}

# Refuse to run if placeholders haven't been replaced
for var in SBOM_LAMBDA_URL SBOM_AUTH_TOKEN SBOM_PRESIGN_SECRET; do
    if [[ "${!var}" == *REPLACE_ME* ]]; then
        echo "ERROR: $var still contains a placeholder. Edit the script before deploying." >&2
        exit 1
    fi
done

echo "=== SBOM Audit Keychain Bootstrap ==="

store_secret "SBOM_LAMBDA_URL"     "$SBOM_LAMBDA_URL"
store_secret "SBOM_AUTH_TOKEN"     "$SBOM_AUTH_TOKEN"
store_secret "SBOM_PRESIGN_SECRET" "$SBOM_PRESIGN_SECRET"

echo ""
echo "All secrets stored in $KEYCHAIN"
echo "Run the main SBOM script to verify end-to-end."
