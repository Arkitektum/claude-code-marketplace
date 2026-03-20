#!/bin/bash
# Prevents Claude from modifying IDE config directories to avoid
# malicious edits (e.g. auto-running commands via tasks/settings).
# Covers: VS Code (.vscode/), JetBrains (.idea/), Visual Studio (.vs/)

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

PROTECTED_DIRS=(".vscode/" ".idea/" ".vs/")

for dir in "${PROTECTED_DIRS[@]}"; do
  if [[ "$FILE_PATH" == *"/$dir"* ]] || [[ "$FILE_PATH" == "$dir"* ]]; then
    echo "Blocked for security reasons: cannot modify IDE config files: $FILE_PATH" >&2
    exit 2
  fi
done

exit 0
