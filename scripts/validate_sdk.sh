#!/bin/bash
set -euo pipefail

# Validates that a Fern generator upgrade produces code that compiles
# in the downstream SDK repo.
#
# Usage: ./scripts/validate_sdk.sh <group> <downstream-repo> <compile-command>
#
# Example: ./scripts/validate_sdk.sh python-sdk schematichq/schematic-python "poetry install && poetry run mypy ."

GROUP="$1"
DOWNSTREAM_REPO="$2"
COMPILE_CMD="$3"

PREVIEW_DIR="fern/.preview"
WORK_DIR=$(mktemp -d)

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

echo "=== Validating $GROUP against $DOWNSTREAM_REPO ==="

# Step 1: Generate preview
echo "Running fern generate --preview for group $GROUP..."
if ! fern generate --group "$GROUP" --preview 2>&1; then
  echo "RESULT:GENERATE_FAILED"
  exit 1
fi

# Step 2: Find the preview output directory
# Fern puts output in fern/.preview/<sanitized-generator-name>/
# where sanitization replaces non-alphanumeric (except - and _) with _
PREVIEW_SUBDIR=$(ls -d "$PREVIEW_DIR"/*/ 2>/dev/null | head -1)
if [ -z "$PREVIEW_SUBDIR" ]; then
  echo "ERROR: No preview output found in $PREVIEW_DIR"
  echo "RESULT:GENERATE_FAILED"
  exit 1
fi
echo "Preview output: $PREVIEW_SUBDIR"

# Step 3: Clone the downstream repo
echo "Cloning $DOWNSTREAM_REPO..."
gh repo clone "$DOWNSTREAM_REPO" "$WORK_DIR/repo" -- --depth 1

# Step 4: Overlay generated files onto the clone
echo "Overlaying preview output..."
rsync -a --exclude='.git' "$PREVIEW_SUBDIR" "$WORK_DIR/repo/"

# Step 5: Run compile check
echo "Running compile check: $COMPILE_CMD"
cd "$WORK_DIR/repo"
if eval "$COMPILE_CMD" 2>&1; then
  echo "RESULT:PASSED"
  exit 0
else
  echo "RESULT:COMPILE_FAILED"
  exit 1
fi
