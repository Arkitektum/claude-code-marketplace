# pii-log-guard

Keeps personal data in log exports out of Claude's context.

Log exports, HAR files and XML payloads can contain national identity numbers (such as Norwegian fødselsnummer), names and addresses. Once Claude has read a file, its content is in the session transcript and cannot be taken back. This plugin makes Claude redact first and read only the redacted copy.

## What it does

**Hook** (`PreToolUse` on `Read`, `Grep` and `Bash`): denies access to data files outside any git repository. Data files are `.csv`, `.ndjson`, `.json`, `.log`, `.txt`, `.xlsx`, `.xml` and `.har`. The deny message tells Claude which tool to run instead.

These are always allowed:

- files inside a git repository
- any `.claude/` directory
- `/tmp/redacted/`, where redacted copies are written
- `/etc/claude-code/`
- the three tools below
- output redirection (`> file.csv`), because writing is not reading

A recursive search over a folder that holds such files is also denied. Narrow it to a repository, or use `--include=*.cs` or a Grep `glob`/`type`.

Writing is not blocked: the `Write` tool and output redirection (`>`, `>>`) work anywhere. Commands that take the file name as an argument (`touch`, `tee`, `cp`, a script's `--out`) are denied outside git repos, because the hook can't tell writing from reading. Keep synthetic test data you need to read back inside a git repository.

**Tools** in `scripts/`. None of them modify the original file.

| Script | For | Output |
| --- | --- | --- |
| `redact-log-export.py <file>` | CSV and text log exports | Copy in `/tmp/redacted/<name>` with identity numbers, e-mail, street addresses, phone numbers and base64 removed. 7–9-digit ids and `userId` values become stable `[ID#n]`. Prints counts and leftover-PII checks by shape. |
| `data-shape.py <file.xml>` | XML payloads | Structure, counts and text lengths only, never values. |
| `har-summary.py <file.har> [--all]` | Browser HAR exports | Method, path, status and timing, plus redacted error fields from failed responses. Never headers, cookies, tokens or bodies. |

## Limits

- The redaction is heuristic and tuned for Norwegian data: 11-digit identity numbers and Norwegian street names. Names in free text are only flagged ("Capitalised word pairs", by shape), not removed. If the report lists findings, inspect them by shape and extend the script. Do not read the file.
- The `Bash` check is best effort. It finds file paths in the command text and follows `cd`. A command written to get around it can.
- The original file stays on disk with all its data. Delete it when you are done.
- The real fix is to keep personal data out of the logs at the source.

## Install

```
/plugin install pii-log-guard@arkitektum-marketplace
```

Requires `python3`. The tools use only the standard library.

## Tests

```
bash tests/block-unredacted-log-reads.test.sh
```

The tests use synthetic files in a temporary folder.
