#!/usr/bin/env python3
"""Summarise a browser HAR file without exposing headers, cookies, tokens or bodies.

Usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/har-summary.py <file.har> [--all]

Prints per request: start offset, method, host, path (query keys only, values
dropped; 7-9 digit ids pseudonymised), status, total time and response size.
For responses with status >= 400 it also prints title/status/detail/type from a
JSON (ProblemDetails) body, or the first 200 chars of a text body - all run
through the redaction rules of redact-log-export.py. Headers, cookies, request
bodies and successful response bodies are never printed.
By default only failed requests, plus a per-path summary, are listed; --all lists every request.
"""
import collections
import datetime as dt
import importlib.util
import json
import os
import re
import sys
from urllib.parse import parse_qsl, urlsplit

_spec = importlib.util.spec_from_file_location(
    "redact", os.path.join(os.path.dirname(os.path.abspath(__file__)), "redact-log-export.py")
)
_redact = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_redact)


def redact(text):
    return _redact.redact(text)[0]


def clean_path(url):
    parts = urlsplit(url)
    keys = [k for k, _ in parse_qsl(parts.query, keep_blank_values=True)]
    path = redact(parts.path)
    return parts.netloc, path + (f"?{'&'.join(keys)}" if keys else "")


def error_body(entry):
    content = entry.get("response", {}).get("content", {}) or {}
    text = content.get("text") or ""
    if content.get("encoding") == "base64" or not text:
        return f"<{content.get('mimeType', '?')}, {content.get('size', 0)} bytes, not shown>"
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            keep = {k: obj[k] for k in ("title", "status", "detail", "type", "message", "error") if k in obj}
            if keep:
                return redact(json.dumps(keep, ensure_ascii=False))[:400]
        if isinstance(obj, str):
            return redact(obj)[:300]
        return f"<json {type(obj).__name__}, {len(text)} chars>"
    except ValueError:
        return redact(re.sub(r"\s+", " ", text))[:200]


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    show_all = "--all" in argv
    with open(argv[0], encoding="utf-8-sig") as fh:
        har = json.load(fh)
    entries = har.get("log", {}).get("entries", [])
    if not entries:
        print("no entries")
        return 1
    t0 = min(dt.datetime.fromisoformat(e["startedDateTime"].replace("Z", "+00:00")) for e in entries)
    per_path = collections.defaultdict(lambda: {"n": 0, "fail": 0, "statuses": collections.Counter(), "ms": []})
    rows = []
    entries = [e for e in entries if not e.get("request", {}).get("url", "").startswith("data:")]
    for e in entries:
        started = dt.datetime.fromisoformat(e["startedDateTime"].replace("Z", "+00:00"))
        method = e.get("request", {}).get("method", "?")
        host, path = clean_path(e.get("request", {}).get("url", ""))
        status = e.get("response", {}).get("status", 0)
        ms = round(e.get("time", 0))
        size = e.get("response", {}).get("content", {}).get("size", 0)
        key = f"{method} {host}{re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '{guid}', path)}"
        p = per_path[key]
        p["n"] += 1
        p["statuses"][status] += 1
        p["ms"].append(ms)
        failed = status >= 400 or status == 0
        p["fail"] += failed
        if show_all or failed:
            rows.append(((started - t0).total_seconds(), method, host, path, status, ms, size, error_body(e) if status >= 400 else ""))

    print(f"entries: {len(entries)}   failed (>=400 or 0): {sum(p['fail'] for p in per_path.values())}\n")
    print("Per endpoint (guids collapsed):")
    for key, p in sorted(per_path.items(), key=lambda kv: (-kv[1]["fail"], -kv[1]["n"])):
        print(f"  {p['n']:>4}x  fail={p['fail']:<4} status={dict(p['statuses'])}  max={max(p['ms'])}ms  {key}")
    print("\nRequests:" if show_all else "\nFailed requests:")
    for off, method, host, path, status, ms, size, body in rows:
        line = f"  +{off:7.2f}s {status:>3} {ms:>6}ms {method:<6} {host}{path}"
        print(line + (f"\n           -> {body}" if body else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
