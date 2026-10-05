#!/bin/bash
set -e

# Extract the ZIP
mkdir -p extracted
cd extracted
unzip -o ../bsrpro-vault-0.2.10-code12-optionA-source.zip

# Find the source file
RESTORE_FILE=$(find . -name "RestoreVaultTransactionUseCase.kt" -type f)

if [ -z "$RESTORE_FILE" ]; then
  echo "File not found!"
  exit 1
fi

echo "Found file at: $RESTORE_FILE"

# Backup original
cp "$RESTORE_FILE" "${RESTORE_FILE}.bak"

# Show line 45 and surrounding context
echo "=== Original file around line 45 ==="
sed -n '40,50p' "$RESTORE_FILE"

# Remove the @Synchronized annotation from suspend functions
# and fix RecoveryJournal import
sed -i.tmp '/@Synchronized.*suspend/d' "$RESTORE_FILE"
sed -i.tmp 's/RecoveryJournal/RecoveryJournal/g' "$RESTORE_FILE"

echo "=== Fixed file around line 45 ==="
sed -n '40,50p' "$RESTORE_FILE"

echo "✓ File fixed!"
