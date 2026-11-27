#!/usr/bin/env python3
"""Print the SHAPE of an XML data file without printing any values.

Usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/data-shape.py <file.xml> [--top N]

Per element path: occurrence count, how many are empty, and text lengths
(max/avg). Values are never printed - only counts, lengths and a character-class
summary (letters/digits/whitespace/control/other) for unusually long texts.
"""
import collections
import sys
import xml.etree.ElementTree as ET


def strip_ns(tag):
    return tag.split("}", 1)[-1]


def char_classes(text):
    c = collections.Counter()
    for ch in text:
        if ch.isalpha():
            c["letters"] += 1
        elif ch.isdigit():
            c["digits"] += 1
        elif ch in " \t\r\n":
            c["whitespace"] += 1
        elif ord(ch) < 32:
            c["CONTROL"] += 1
        else:
            c["other"] += 1
    return dict(c)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    path = argv[0]
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 40

    stats = collections.defaultdict(lambda: {"n": 0, "empty": 0, "lens": [], "attrs": collections.Counter()})
    long_texts = []
    root = ET.parse(path).getroot()

    def walk(el, prefix):
        p = f"{prefix}/{strip_ns(el.tag)}"
        s = stats[p]
        s["n"] += 1
        text = (el.text or "").strip()
        if len(el) == 0:
            if not text:
                s["empty"] += 1
            else:
                s["lens"].append(len(text))
                if len(text) > 500:
                    long_texts.append((len(text), p, char_classes(text)))
        for a in el.attrib:
            s["attrs"][strip_ns(a)] += 1
        for child in el:
            walk(child, p)

    walk(root, "")
    print(f"root: {strip_ns(root.tag)}   distinct paths: {len(stats)}   elements: {sum(s['n'] for s in stats.values())}")
    print(f"{'count':>7} {'empty':>6} {'maxlen':>7} {'avglen':>7}  path")
    rows = sorted(stats.items(), key=lambda kv: (-kv[1]["n"], kv[0]))
    for p, s in rows[:top]:
        lens = s["lens"]
        mx = max(lens) if lens else 0
        avg = round(sum(lens) / len(lens), 1) if lens else 0
        attrs = f"  attrs={dict(s['attrs'])}" if s["attrs"] else ""
        print(f"{s['n']:>7} {s['empty']:>6} {mx:>7} {avg:>7}  {p}{attrs}")
    if len(rows) > top:
        print(f"... {len(rows) - top} more paths (use --top)")
    if long_texts:
        print("\nLong texts (>500 chars), by path - character classes only:")
        for ln, p, cc in sorted(long_texts, reverse=True)[:15]:
            print(f"  {ln:>8}  {p}  {cc}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
