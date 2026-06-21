#!/usr/bin/env bash
# install_deps.sh
# Termux-friendly automated dependency installer for PythonCHAT-AI
# - Reads requirements.txt in the repo and installs missing pip packages
# - Skips packages already installed
# - On install errors, tries common fixes (upgrade pip/setuptools/wheel)
# - If still failing, collects logs and creates a patch archive (install_patch_<ts>.tar.gz)
#
# Usage:
#   chmod +x install_deps.sh
#   ./install_deps.sh
#
# Notes:
# - This script tries safe automatic fixes but will not force-install large system packages
#   without notifying the user. It prints instructions when manual intervention may be needed.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQ_FILE="$SCRIPT_DIR/requirements.txt"
PATCH_DIR_BASE="$SCRIPT_DIR/install_patches"
TS=$(date -u +%Y%m%dT%H%M%SZ)
LOG_FILE="/tmp/install_deps_${TS}.log"
PATCH_NAME="install_patch_${TS}.tar.gz"

echo "[install_deps] Starting at $(date -u)"
echo "[install_deps] Log -> $LOG_FILE"

mkdir -p "$SCRIPT_DIR" "$PATCH_DIR_BASE"

# Ensure python3 and pip exist
if ! command -v python3 >/dev/null 2>&1; then
  echo "[install_deps] python3 not found. Attempting to install via Termux pkg..." | tee -a "$LOG_FILE"
  if command -v pkg >/dev/null 2>&1; then
    echo "[install_deps] Running: pkg install -y python" | tee -a "$LOG_FILE"
    pkg install -y python 2>&1 | tee -a "$LOG_FILE" || true
  else
    echo "[install_deps] pkg not found. Please install Python manually." | tee -a "$LOG_FILE"
    exit 1
  fi
fi

# Prefer pip via python -m pip
PIP_CMD="python3 -m pip"

# Upgrade pip/setuptools/wheel first (best-effort)
echo "[install_deps] Upgrading pip, setuptools, wheel (best effort)" | tee -a "$LOG_FILE"
$PIP_CMD install --upgrade pip setuptools wheel 2>&1 | tee -a "$LOG_FILE" || echo "[install_deps] pip upgrade encountered an error; continuing" | tee -a "$LOG_FILE"

if [ ! -f "$REQ_FILE" ]; then
  echo "[install_deps] requirements.txt not found at $REQ_FILE" | tee -a "$LOG_FILE"
  echo "[install_deps] Nothing to do." | tee -a "$LOG_FILE"
  exit 0
fi

# Parse requirements file into array of package specs
mapfile -t PKGS < <(grep -E -v '^(#|\s*$)' "$REQ_FILE" | sed 's/#.*$//')

if [ ${#PKGS[@]} -eq 0 ]; then
  echo "[install_deps] No packages listed in requirements.txt" | tee -a "$LOG_FILE"
  exit 0
fi

FAILED_PACKAGES=()

for spec in "${PKGS[@]}"; do
  # Extract package name for checking (strip version specifiers)
  pkgname=$(echo "$spec" | sed -E 's/\s*([A-Za-z0-9_.\-]+).*/\1/')
  echo "[install_deps] Checking package: $spec (test name: $pkgname)" | tee -a "$LOG_FILE"

  # Check if installed via pip show
  if $PIP_CMD show "$pkgname" >/dev/null 2>&1; then
    echo "[install_deps] -> already installed: $pkgname" | tee -a "$LOG_FILE"
    continue
  fi

  echo "[install_deps] -> not installed, attempting: $PIP_CMD install $spec" | tee -a "$LOG_FILE"
  if $PIP_CMD install --no-cache-dir "$spec" 2>&1 | tee -a "$LOG_FILE"; then
    echo "[install_deps] Installed: $spec" | tee -a "$LOG_FILE"
    continue
  fi

  echo "[install_deps] Initial install failed for $spec; attempting automatic fixes" | tee -a "$LOG_FILE"

  # Attempt fixes: upgrade pip tools again
  echo "[install_deps] Trying to upgrade build tools (pip/setuptools/wheel) and retry" | tee -a "$LOG_FILE"
  $PIP_CMD install --upgrade pip setuptools wheel 2>&1 | tee -a "$LOG_FILE" || true

  # Retry install
  if $PIP_CMD install --no-cache-dir "$spec" 2>&1 | tee -a "$LOG_FILE"; then
    echo "[install_deps] Installed after upgrade: $spec" | tee -a "$LOG_FILE"
    continue
  fi

  # Try installing with --no-binary to force source build (may fail if build deps missing)
  echo "[install_deps] Retry with --no-binary :all: for $spec" | tee -a "$LOG_FILE"
  if $PIP_CMD install --no-binary :all: "$spec" 2>&1 | tee -a "$LOG_FILE"; then
    echo "[install_deps] Installed via source build: $spec" | tee -a "$LOG_FILE"
    continue
  fi

  # Last resort: attempt common Termux build deps (user will be informed)
  if command -v pkg >/dev/null 2>&1; then
    echo "[install_deps] Attempting to install common Termux build deps: clang, make, openssl-dev, libffi-dev" | tee -a "$LOG_FILE"
    pkg install -y clang make openssl-dev libffi-dev 2>&1 | tee -a "$LOG_FILE" || true
    echo "[install_deps] Retrying pip install after installing build deps" | tee -a "$LOG_FILE"
    if $PIP_CMD install --no-cache-dir "$spec" 2>&1 | tee -a "$LOG_FILE"; then
      echo "[install_deps] Installed after adding build deps: $spec" | tee -a "$LOG_FILE"
      continue
    fi
  fi

  echo "[install_deps] All automatic attempts failed for $spec" | tee -a "$LOG_FILE"
  FAILED_PACKAGES+=("$spec")

done

# Summary
if [ ${#FAILED_PACKAGES[@]} -eq 0 ]; then
  echo "[install_deps] All packages installed successfully or already present." | tee -a "$LOG_FILE"
  exit 0
fi

echo "[install_deps] The following packages failed to install:" | tee -a "$LOG_FILE"
for f in "${FAILED_PACKAGES[@]}"; do
  echo "  - $f" | tee -a "$LOG_FILE"
done

# Create patch bundle for failed installs
PATCH_DIR="$PATCH_DIR_BASE/patch_$TS"
mkdir -p "$PATCH_DIR"

echo "failed_packages" > "$PATCH_DIR/failed_packages.txt"
for f in "${FAILED_PACKAGES[@]}"; do
  echo "$f" >> "$PATCH_DIR/failed_packages.txt"
done

# Save the requirements file and the log
cp "$REQ_FILE" "$PATCH_DIR/requirements_snapshot.txt"
cp "$LOG_FILE" "$PATCH_DIR/install_error_log.txt"

# Create a simple helper script in the patch dir to attempt install on another machine
cat > "$PATCH_DIR/README.txt" <<'EOF'
This patch archive contains the list of packages that failed to install on the source device
and a log file describing the failure.

To attempt repair on another machine:
  1. Inspect install_error_log.txt for error details.
  2. Copy requirements_snapshot.txt to the target machine.
  3. Run: python3 -m pip install --upgrade pip setuptools wheel
  4. Run: python3 -m pip install -r requirements_snapshot.txt

If the error is due to missing system libraries, install platform-specific build deps (e.g., on Debian/Ubuntu:
  sudo apt update && sudo apt install -y build-essential libssl-dev libffi-dev python3-dev)

EOF

# Pack the patch
( cd "$PATCH_DIR_BASE" && tar -czf "$PATCH_NAME" "patch_$TS" )
MV_TO="$SCRIPT_DIR/$PATCH_NAME"
mv "$PATCH_DIR_BASE/$PATCH_NAME" "$MV_TO" 2>/dev/null || true

echo "[install_deps] Created patch archive: $MV_TO" | tee -a "$LOG_FILE"

echo "[install_deps] Done. Please review $MV_TO and install_error_log.txt for details." | tee -a "$LOG_FILE"

echo "[install_deps] EXIT: non-zero due to failed installs" | tee -a "$LOG_FILE"
exit 2
