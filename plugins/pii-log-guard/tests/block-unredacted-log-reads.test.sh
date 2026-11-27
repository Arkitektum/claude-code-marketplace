#!/usr/bin/env bash
# Test matrix for the block-unredacted-log-reads PreToolUse hook. Synthetic files only.
H="$(cd "$(dirname "$0")/../scripts" && pwd)/block-unredacted-log-reads.py"
pass=0; fail=0

W=$(mktemp -d)
trap 'rm -rf "$W"' EXIT
mkdir -p "$W/ws/.claude" "$W/ws/repo/.git" "$W/ws/repo/src" "$W/ws/sub/repo2/.git" "$W/ws/other"
touch "$W/ws/.claude/settings.local.json" "$W/ws/export.csv" "$W/ws/export 2.csv" "$W/ws/notes.md" "$W/ws/sub/loose.ndjson" \
      "$W/ws/repo/data.json" "$W/ws/repo/src/App.cs" "$W/ws/sub/repo2/log.txt" "$W/ws/other/script.ps1"
mkdir -p /tmp/redacted && touch /tmp/redacted/hooktest-export.csv

t() { # $1=expected(DENY|ALLOW) $2=tool $3=tool_input-json $4=label [$5=cwd]
  local cwd=${5:-$W/ws}
  out=$(jq -n --arg t "$2" --argjson i "$3" --arg c "$cwd" '{tool_name:$t,tool_input:$i,cwd:$c}' | python3 "$H")
  if [ -z "$out" ]; then got=ALLOW; else got=DENY; fi
  if [ "$got" = "$1" ]; then
    printf '  ok   %-6s %s\n' "$got" "$4"; pass=$((pass+1))
  else
    printf '  FAIL exp=%s got=%s  %s\n' "$1" "$got" "$4"; fail=$((fail+1))
  fi
}
j() { jq -n --arg v "$2" "{$1: \$v}"; }

echo "Deny cases:"
t DENY Read "$(j file_path "$W/ws/export.csv")" "Read export outside repo"
t DENY Read "$(j file_path export.csv)" "Read relative path"
t DENY Read "$(j file_path "$W/ws/sub/loose.ndjson")" "Read ndjson in non-repo subdir"
t DENY Bash "$(j command 'cat export.csv')" "cat export"
t DENY Bash "$(j command 'head -1 "export 2.csv"')" "head quoted name with spaces"
t DENY Bash "$(j command "ls && python3 -c \"open('export.csv').read()\"")" "python open in 2nd segment"
t DENY Bash "$(j command "cd $W/ws/sub && wc -l loose.ndjson; cat loose.ndjson")" "cd tracked, then cat"
t DENY Bash "$(j command "python3 - <<'EOF'
import csv
rows=list(csv.reader(open('$W/ws/export.csv')))
EOF")" "heredoc reads export"
t DENY Bash "$(j command 'cat *.csv')" "glob expands to export"
t DENY Bash "$(j command "grep -rn foo $W/ws")" "recursive grep over non-repo dir"
t DENY Bash "$(j command 'rg foo')" "rg from non-repo cwd"
t DENY Bash "$(j command 'find . -name "*.csv" -exec cat {} +')" "find -exec cat"
t DENY Grep '{"pattern":"x"}' "Grep tool, default path = non-repo cwd"
t DENY Grep "$(j path "$W/ws/export.csv")" "Grep tool on export file"
t DENY Grep "$(jq -n --arg p "$W/ws" '{pattern:"x",path:$p,glob:"*.{csv,cs}"}')" "Grep glob incl csv"

echo "Allow cases:"
t ALLOW Read "$(j file_path "$W/ws/repo/data.json")" "json inside repo"
t ALLOW Read "$(j file_path "$W/ws/sub/repo2/log.txt")" "txt inside nested repo"
t ALLOW Read "$(j file_path "$W/ws/notes.md")" "non-data file outside repo"
t ALLOW Read "$(j file_path /tmp/redacted/hooktest-export.csv)" "redacted copy"
t ALLOW Read "$(j file_path "$HOME/.claude/settings.json")" "~/.claude allowlisted"
t ALLOW Read "$(j file_path "$W/ws/.claude/settings.local.json")" "project .claude/ allowlisted"
t ALLOW Bash "$(j command "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/redact-log-export.py export.csv 'export 2.csv'")" "the redaction script"
t ALLOW Bash "$(j command 'ls -la *.csv; wc -l export.csv; stat export.csv')" "metadata only"
t ALLOW Bash "$(j command 'find . -maxdepth 2 -newer export.csv -name "*.csv"')" "find without -exec"
t ALLOW Bash "$(j command "cd /tmp/redacted && python3 -c \"open('hooktest-export.csv')\"")" "cd into redacted, read copy"
t ALLOW Bash "$(j command 'cat repo/data.json')" "cat json in repo"
t ALLOW Bash "$(j command "grep -rn --include=*.cs foo $W/ws")" "recursive grep limited to *.cs"
t ALLOW Bash "$(j command 'rg foo repo')" "rg inside repo"
t ALLOW Bash "$(j command 'cat notes.md')" "cat non-data file"
t ALLOW Bash "$(j command "python3 -c \"open(f'{app}/meta.json')\"")" "template placeholder path is not a file"
t ALLOW Bash "$(j command 'grep -rl --include=*.cs --include=*.json foo repo')" "--include=*.json is a pattern, not a file"
t ALLOW Bash "$(j command "rg -g '*.csv' foo repo")" "-g pattern inside repo"
t DENY Bash "$(j command 'grep -rl --include=*.csv foo .')" "--include=*.csv over non-repo dir still blocked"
t ALLOW Bash "$(j command 'find repo -name "*.json" -exec cat {} +')" "find -exec inside repo"
t ALLOW Bash "$(j command 'printf "a;b" > export.csv; echo x >> export.csv')" "redirect target is written, not read"
t DENY Bash "$(j command 'sort < export.csv > /tmp/out.txt')" "input redirect still blocked"
t ALLOW Grep "$(jq -n --arg p "$W/ws" '{pattern:"x",path:$p,type:"cs"}')" "Grep type=cs"
t ALLOW Grep "$(jq -n --arg p "$W/ws/repo" '{pattern:"x",path:$p}')" "Grep inside repo"
t ALLOW Grep '{"pattern":"x"}' "Grep from repo cwd" "$W/ws/repo"

echo "Writing test files (documents current behaviour):"
t ALLOW Write "$(jq -n --arg p "$W/ws/new.csv" '{file_path:$p,content:"a;b"}')" "Write tool creates a data file"
t ALLOW Bash "$(j command 'python3 gen.py 50 > new.xml')" "generator output redirected with >"
t DENY Bash "$(j command 'touch new.csv')" "touch: file name looks like a read"
t DENY Bash "$(j command 'python3 gen.py --out new.csv')" "script given the output path as an argument"
t DENY Bash "$(j command 'cp export.csv copy.csv')" "cp reads the source"
t DENY Read "$(j file_path "$W/ws/new.csv")" "reading the new file back"
t ALLOW Bash "$(j command 'cat repo/data.json')" "data files inside a git repo are unrestricted"

rm -f /tmp/redacted/hooktest-export.csv
echo "pass=$pass fail=$fail"
[ "$fail" -eq 0 ]
