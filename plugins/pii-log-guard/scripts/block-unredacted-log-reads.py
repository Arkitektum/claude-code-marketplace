#!/usr/bin/env python3
"""PreToolUse hook: refuse reads of data files that live outside any git repo.

Log exports (CSV, NDJSON, HAR, XML payloads) land outside repos and can carry national
identity numbers and other personal data.
They must go through scripts/redact-log-export.py (next to this file) first; only
the copy in /tmp/redacted/ may be read. Covers Read, Grep and Bash (best effort: paths are
picked out of the command text).

Reads hook payload JSON on stdin. Silence + exit 0 means "allow".
"""
import fnmatch
import glob
import json
import os
import re
import sys

DATA_EXTS = ("csv", "ndjson", "json", "log", "txt", "xlsx", "xml", "har")
HOME = os.path.expanduser("~")
ALLOW_PREFIXES = (
    os.path.join(HOME, ".claude") + os.sep,
    "/tmp/redacted" + os.sep,
    "/etc/claude-code" + os.sep,
)
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REDACT_SCRIPT = os.path.join(SCRIPTS_DIR, "redact-log-export.py")
SHAPE_SCRIPT = os.path.join(SCRIPTS_DIR, "data-shape.py")
HAR_SCRIPT = os.path.join(SCRIPTS_DIR, "har-summary.py")
# Commands that only touch metadata, never contents.
METADATA_CMDS = {"ls", "wc", "stat", "du", "test", "[", "file", "mkdir", "echo", "printf", "cd", "pwd"}
GREP_CMDS = {"grep", "egrep", "fgrep", "rg", "ag"}
SKIP_DIRS = {".git", "node_modules", "bin", "obj"}
MAX_SCAN_DEPTH = 6

EXT_ALT = "|".join(DATA_EXTS)
PATH_TOKEN_RE = re.compile(
    rf"""(['"])([^'"\n]*?\.(?:{EXT_ALT}))\1|([^\s'"()<>|;&=,]+\.(?:{EXT_ALT}))(?![\w.])""",
    re.IGNORECASE,
)

_repo_cache = {}


def is_data_file(path):
    return path.lower().rsplit(".", 1)[-1] in DATA_EXTS if "." in os.path.basename(path) else False


def in_repo(path):
    d = path if os.path.isdir(path) else os.path.dirname(path)
    d = os.path.abspath(d)
    seen = []
    while True:
        if d in _repo_cache:
            result = _repo_cache[d]
            break
        seen.append(d)
        if os.path.exists(os.path.join(d, ".git")):
            result = True
            break
        parent = os.path.dirname(d)
        if parent == d:
            result = False
            break
        d = parent
    for s in seen:
        _repo_cache[s] = result
    return result


def allowlisted(path):
    if f"{os.sep}.claude{os.sep}" in path + os.sep:
        return True
    return any((path + os.sep).startswith(p) or path.startswith(p) for p in ALLOW_PREFIXES)


def resolve(token, cwd):
    p = os.path.expandvars(os.path.expanduser(token))
    if not os.path.isabs(p):
        p = os.path.join(cwd, p)
    return os.path.normpath(p)


def needs_redaction(path):
    return is_data_file(path) and not allowlisted(path) and not in_repo(path)


def expand_braces(pattern):
    m = re.search(r"\{([^{}]*)\}", pattern)
    if not m:
        return [pattern]
    out = []
    for alt in m.group(1).split(","):
        out.extend(expand_braces(pattern[: m.start()] + alt + pattern[m.end():]))
    return out


def scan_dir(root, globs=None):
    """Data files under root that are outside any repo. Repos are pruned."""
    if allowlisted(root + os.sep) or in_repo(root):
        return []
    patterns = [p for g in (globs or []) for p in expand_braces(g)]
    found = []
    root_depth = root.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root):
        if os.path.exists(os.path.join(dirpath, ".git")):
            dirnames[:] = []
            continue
        if dirpath.count(os.sep) - root_depth >= MAX_SCAN_DEPTH:
            dirnames[:] = []
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if not is_data_file(f):
                continue
            if patterns and not any(fnmatch.fnmatch(f, p) or fnmatch.fnmatch(os.path.join(dirpath, f), p) for p in patterns):
                continue
            full = os.path.join(dirpath, f)
            if not allowlisted(full):
                found.append(full)
    return found


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def deny_file(path):
    name = os.path.basename(path)
    deny(
        f"Blocked: '{path}' is a data file outside any git repo - likely a log export containing PII "
        f"(fnr, names, addresses). Redact it first: python3 {REDACT_SCRIPT} '{path}' "
        f"- then read ONLY '/tmp/redacted/{name}'. If the script reports leftover findings, inspect them "
        f"by shape and extend the script before reading. Never modify the original. "
        f"For XML payloads use python3 {SHAPE_SCRIPT} '{path}' (structure only); for browser .har files "
        f"use python3 {HAR_SCRIPT} '{path}' (no headers, cookies or bodies)."
    )


def deny_dir(root, found):
    sample = ", ".join(os.path.basename(f) for f in found[:3])
    deny(
        f"Blocked: searching '{root}' would read {len(found)} data file(s) outside any git repo "
        f"(e.g. {sample}) that may hold PII. Narrow the search to a repo path or add a glob/--include "
        f"that excludes them, or redact first with python3 {REDACT_SCRIPT} <file> and search /tmp/redacted/."
    )


def check_path(path):
    if os.path.isdir(path) or re.search(r"\{[^{}/]*\}", path):
        return  # directory, or a template placeholder such as {app} - not a real file
    if any(c in path for c in "*?["):
        matches = glob.glob(path)
        for m in matches:
            if needs_redaction(m):
                deny_file(m)
        if not matches and needs_redaction(path):
            deny_file(path)
        return
    if needs_redaction(path):
        deny_file(path)


def split_segments(command):
    return [s.strip() for s in re.split(r"\|\||&&|[;|&\n]", command) if s.strip()]


def words(segment):
    return re.findall(r"""'[^']*'|"[^"]*"|\S+""", segment)


def unquote(w):
    return w[1:-1] if len(w) >= 2 and w[0] == w[-1] and w[0] in "'\"" else w


def check_grep(ws, cwd):
    cmd = os.path.basename(ws[0])
    recursive = cmd in {"rg", "ag"} or any(
        w in ("--recursive", "--dereference-recursive") or re.fullmatch(r"-[a-zA-Z]*[rR][a-zA-Z]*", w) for w in ws[1:]
    )
    if not recursive:
        return
    globs = []
    args = []
    i = 1
    while i < len(ws):
        w = unquote(ws[i])
        if w.startswith("--include="):
            globs.append(w.split("=", 1)[1])
        elif w in ("-g", "--glob", "--include") and i + 1 < len(ws):
            globs.append(unquote(ws[i + 1]))
            i += 1
        elif not w.startswith("-"):
            args.append(w)
        i += 1
    dirs = [resolve(a, cwd) for a in args if os.path.isdir(resolve(a, cwd))]
    for d in dirs or [cwd]:
        found = scan_dir(d, globs)
        if found:
            deny_dir(d, found)


def check_find(ws, cwd):
    roots, globs = [], []
    i = 1
    while i < len(ws) and not ws[i].startswith(("-", "(", "!")):
        roots.append(resolve(unquote(ws[i]), cwd))
        i += 1
    for j, w in enumerate(ws):
        if w in ("-name", "-iname") and j + 1 < len(ws):
            globs.append(unquote(ws[j + 1]))
    for d in roots or [cwd]:
        found = scan_dir(d, globs) if os.path.isdir(d) else ([d] if needs_redaction(d) else [])
        if found:
            deny_dir(d, found)


def check_bash(command, cwd):
    for seg in split_segments(command):
        if any(s in seg for s in ("redact-log-export.py", "data-shape.py", "har-summary.py")):
            continue
        ws = words(seg)
        if not ws:
            continue
        cmd = os.path.basename(unquote(ws[0]))
        if cmd == "cd":
            target = unquote(ws[1]) if len(ws) > 1 else HOME
            cwd = resolve(target, cwd)
            continue
        if cmd == "find":
            if any(w in ("-exec", "-execdir", "-ok", "-okdir") for w in ws):
                check_find(ws, cwd)
            continue
        if cmd in METADATA_CMDS:
            continue
        if cmd in GREP_CMDS:
            check_grep(ws, cwd)
        for m in PATH_TOKEN_RE.finditer(seg):
            before = seg[: m.start()]
            if re.search(r"(?<!<)>>?\s*$", before):
                continue  # output redirection target: written, not read
            if any(ch in m.group(0) for ch in "*?[") and re.search(
                r"(=|(^|\s)(-g|--glob|--include|--exclude|-name|-iname|-path|-ipath)\s+)$", before
            ):
                continue  # search pattern for a flag, not a file
            token = m.group(2) or m.group(3)
            check_path(resolve(token, cwd))


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.getcwd()

    if tool == "Read":
        f = ti.get("file_path") or ""
        if f:
            check_path(resolve(f, cwd))
    elif tool == "Grep":
        p = resolve(ti.get("path") or cwd, cwd)
        if os.path.isfile(p):
            check_path(p)
            return
        t = (ti.get("type") or "").lower()
        if t and t not in DATA_EXTS:
            return
        globs = [ti["glob"]] if ti.get("glob") else (["*." + t] if t else [])
        found = scan_dir(p, globs)
        if found:
            deny_dir(p, found)
    elif tool == "Bash":
        check_bash(ti.get("command") or "", cwd)


if __name__ == "__main__":
    main()
