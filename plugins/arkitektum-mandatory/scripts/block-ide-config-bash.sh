#!/bin/bash
# Prevents Bash commands from modifying IDE config files.
# Covers: VS Code (.vscode/), JetBrains (.idea/), Visual Studio (.vs/)

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

PROTECTED_FILES=(
  ".vscode/settings.json"
  ".vscode/tasks.json"
  ".vscode/launch.json"
  ".vscode/extensions.json"
  ".vscode/keybindings.json"
  ".idea/workspace.xml"
  ".idea/modules.xml"
  ".idea/vcs.xml"
  ".idea/runConfigurations/"
  ".vs/launch.vs.json"
  ".vs/tasks.vs.json"
  ".vs/settings/"
)

for file in "${PROTECTED_FILES[@]}"; do
  if [[ "$COMMAND" == *"$file"* ]]; then
    echo "Blocked for security reasons: Bash command references $file" >&2
    exit 2
  fi
done

exit 0
