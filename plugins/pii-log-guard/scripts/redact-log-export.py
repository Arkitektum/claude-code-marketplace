#!/usr/bin/env python3
"""Redact PII from a log export and write a copy to /tmp/redacted/<name>.

Usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/redact-log-export.py <file> [<file> ...]

The original is never modified. Only the redacted copy may be read afterwards
(the pii-log-guard hook enforces this). The report printed here
contains counts and value *shapes* only, never values.
"""
import collections
import os
import re
import sys

OUT_DIR = "/tmp/redacted"

GUID_RE = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
TIMESTAMP_RE = r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?Z?"
STREET_SUFFIXES = "veien|vegen|gata|gate|vei|veg|bakken|stien|plassen|lia|haugen|tunet|åsen|alleen|svingen"

# All-caps words that are protocol/tech tokens, not names.
TECH_CAPS = set(
    "HTTP HTTPS GET POST PUT PATCH DELETE HEAD OPTIONS API JSON XML PDF ID OK URL URI SQL GUID "
    "UTC UTF NULL TRUE FALSE ERROR WARN INFO DEBUG TRACE FATAL AND OR NOT TLS SSL DNS TCP IP".split()
)
# Capitalised words that are common in log messages; anything else in a "Word Word" pair is suspect.
TECH_WORDS = set(
    "App Core Api Storage Signing Service Task Process Instance Instances Data Error Exception "
    "Internal Server Request Response Http Client Unhandled An Microsoft System Net Sockets Object Value "
    "Null Reference Invalid Operation Signature Type Platform Authorization Authentication Controller "
    "Actions Content Length Bad Gateway Not Found The A Failed Unable Faulty Configuration Sign Get Post "
    "Put Delete Element Elements Pdf Generator Timeout Canceled Cancelled Unauthorized Forbidden Conflict "
    "Gateway Unavailable Too Many Requests Method Allowed Unsupported Media Unprocessable Entity Payload "
    "Large Gone Precondition Required Expectation Failure Created Accepted No Moved Permanently Found "
    "Apm Event Events Azure Function Functions Bus Queue Topic Message Dead Letter Start End "
    "Sending Received Processing Information Warning Debug Trace Critical None".split()
)
SUSPICIOUS_KEY_RE = (
    r'"(\w*(?:[Nn]avn|[Nn]ame|[Pp]erson|[Ii]dentity|[Ff]oedsel|[Ff]nr|[Tt]elefon|[Pp]hone|'
    r'[Aa]dresse|[Aa]ddress|[Ss]sn|[Ee]post|[Mm]ail)\w*)"\s*:\s*"(?!\[)'
)


def shape(s):
    return re.sub(r"[0-9]", "9", re.sub(r"[^\W\d_]", "a", s))


def redact(text):
    protected = {}

    def protect(m):
        key = f"\x00P{len(protected)}\x00"
        protected[key] = m.group(0)
        return key

    text = re.sub(GUID_RE, protect, text)
    text = re.sub(TIMESTAMP_RE, protect, text)

    counts = collections.Counter()
    ids = {}

    def sub(pattern, repl, label, flags=0):
        nonlocal text

        def f(m):
            counts[label] += 1
            return repl(m) if callable(repl) else repl

        text = re.sub(pattern, f, text, flags=flags)

    def pseudonym(m):
        v = m.group(0)
        ids.setdefault(v, f"[ID#{len(ids) + 1}]")
        return ids[v]

    sub(r"(?<!\d)\d{6}\s?\d{5}(?!\d)", "[FNR]", "fnr")
    sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[EMAIL]", "email")
    sub(r"(Address=)[^,;}\]]*", lambda m: m.group(1) + "[ADDR]", "Address=")
    sub(r"[A-Za-z0-9+/]{60,}={0,2}", "[B64]", "base64")
    sub(r"(\+47\s?)?(?<!\d)\d{2}\s\d{2}\s\d{2}\s\d{2}(?!\d)", "[PHONE]", "phone")
    sub(r"(?<!\d)\d{7,9}(?!\d)", pseudonym, "7-9 digit id")
    sub(r"(?<=userId\"\":)\d+|(?<=userId\":)\d+|(?<=userId\": )\d+", pseudonym, "userId")
    sub(rf"\b[A-ZÆØÅ][a-zæøå]+(?:{STREET_SUFFIXES})\s+\d+\s?[A-Za-z]?\b", "[STREET]", "street")

    for key, value in protected.items():
        text = text.replace(key, value)
    return text, counts, len(ids)


def report(text):
    """Leftover-PII checks. Prints counts and shapes only."""
    findings = []
    runs = re.findall(r"(?<![\w-])\d{6,}(?![\w-])", text)
    if runs:
        findings.append(f"digit runs >=6 left: {len(runs)} (lengths {sorted({len(r) for r in runs})})")

    caps = collections.Counter()
    for seq in re.findall(r"\b[A-ZÆØÅ]{2,}(?:\s+[A-ZÆØÅ]{2,})+\b", text):
        words = seq.split()
        if not all(w in TECH_CAPS for w in words):
            caps[" ".join(w if w in TECH_CAPS else shape(w) for w in words)] += 1
    if caps:
        findings.append(f"ALL-CAPS sequences (possible names), by shape: {dict(caps)}")

    pairs = collections.Counter()
    for pair in re.findall(r"\b[A-ZÆØÅ][a-zæøå]+ [A-ZÆØÅ][a-zæøå]+\b", text):
        words = pair.split()
        if not all(w in TECH_WORDS for w in words):
            pairs[" ".join(w if w in TECH_WORDS else shape(w) for w in words)] += 1
    if pairs:
        findings.append(f"Capitalised word pairs (possible names), by shape: {dict(pairs)}")

    keys = collections.Counter(re.findall(SUSPICIOUS_KEY_RE, text))
    if keys:
        findings.append(f"JSON keys with unredacted string values: {dict(keys)}")
    return findings


def main(paths):
    if not paths:
        print(__doc__)
        return 2
    os.makedirs(OUT_DIR, exist_ok=True)
    status = 0
    for src in paths:
        if src.lower().endswith(".xlsx"):
            print(f"{src}: .xlsx is not supported - export as CSV instead.")
            status = 1
            continue
        with open(src, encoding="utf-8-sig", errors="replace") as fh:
            original = fh.read()
        text, counts, distinct_ids = redact(original)
        dst = os.path.join(OUT_DIR, os.path.basename(src))
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(text)

        header = text.splitlines()[0] if text else ""
        header_note = header if len(header) <= 300 else f"<{len(header)} chars, not shown>"
        print(f"== {src}")
        print(f"   lines: {original.count(chr(10))}, header: {header_note}")
        print(f"   redacted: {dict(counts) or 'nothing'}; distinct pseudonymised ids: {distinct_ids}")
        findings = report(text)
        if findings:
            print("   CHECK BEFORE READING (inspect by shape, extend the script if real PII):")
            for f in findings:
                print(f"   - {f}")
        else:
            print("   leftover checks: clean")
        print(f"   -> read only: {dst}")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
