#!/usr/bin/env python3
"""
Fetch latest version and license for a third-party package via deps.dev,
walk the transitive dependency graph, report a license per node, and
print a summary of total transitive deps and the union of licenses found.

A curated overrides.json next to this script supplies licenses for packages
whose upstream metadata is unparseable (deps.dev returns "non-standard")
or missing ("UNKNOWN"). Overrides are reported with a "(override)" suffix.

Usage: check-package.py <pypi|npm|cargo|nuget|go> <name>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API = "https://api.deps.dev/v3"
ECOSYSTEMS = ("pypi", "npm", "cargo", "nuget", "go")
OVERRIDE_FILE = Path(__file__).parent / "overrides.json"


class _NotFound:
    """Sentinel: deps.dev returned 404 (distinct from network/parse failure)."""


NOT_FOUND = _NotFound()


def fetch(url: str) -> dict[str, Any] | _NotFound | None:
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return NOT_FOUND
        return None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def enc(s: str) -> str:
    return urllib.parse.quote(s, safe="")


def normalize_name(system: str, name: str) -> str:
    name = name.lower()
    if system == "pypi":
        name = re.sub(r"[-_.]+", "-", name)
    return name


def load_overrides() -> dict[str, dict[str, str]]:
    if not OVERRIDE_FILE.exists():
        return {}
    try:
        data = json.loads(OVERRIDE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    return {
        eco.lower(): {normalize_name(eco.lower(), k): v for k, v in pkgs.items()}
        for eco, pkgs in data.items()
    }


def needs_override(license_text: str) -> bool:
    return "non-standard" in license_text or "UNKNOWN" in license_text


def resolve_license(
    version_doc: dict[str, Any] | None,
    system: str,
    name: str,
    overrides: dict[str, dict[str, str]],
) -> tuple[str, list[str]]:
    """Return (display string, license tokens for the union set)."""
    if version_doc is None:
        base, tokens = "UNKNOWN (lookup failed)", ["UNKNOWN"]
    else:
        licenses = version_doc.get("licenses") or []
        if licenses:
            base, tokens = " OR ".join(licenses), list(licenses)
        else:
            base, tokens = "UNKNOWN", ["UNKNOWN"]

    if needs_override(base):
        override = overrides.get(system, {}).get(normalize_name(system, name))
        if override:
            return f"{override} (override)", [override]

    return base, tokens


def homepage(version_doc: dict[str, Any]) -> str:
    by_label = {
        link.get("label"): link.get("url", "")
        for link in version_doc.get("links") or []
    }
    for label in ("HOMEPAGE", "SOURCE_REPO", "ORIGIN"):
        if url := by_label.get(label, ""):
            return url
    return ""


def default_version(pkg_doc: dict[str, Any]) -> str | None:
    versions = pkg_doc.get("versions") or []
    for v in versions:
        if v.get("isDefault"):
            return v["versionKey"]["version"]
    if versions:
        versions.sort(key=lambda v: v.get("publishedAt") or "")
        return versions[-1]["versionKey"]["version"]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Look up package version, license, and transitive license summary via deps.dev."
    )
    parser.add_argument("ecosystem", choices=ECOSYSTEMS)
    parser.add_argument("name")
    args = parser.parse_args()

    overrides = load_overrides()
    system: str = args.ecosystem
    name: str = args.name

    pkg = fetch(f"{API}/systems/{system}/packages/{enc(name)}")
    if not isinstance(pkg, dict):
        print(
            f"lookup failed for {system}/{name} (not found on deps.dev?)",
            file=sys.stderr,
        )
        return 1

    version = default_version(pkg)
    if not version:
        print(f"no version found for {system}/{name}", file=sys.stderr)
        return 1

    ver = fetch(f"{API}/systems/{system}/packages/{enc(name)}/versions/{enc(version)}")
    if not isinstance(ver, dict):
        print(f"lookup failed for {system}/{name}@{version}", file=sys.stderr)
        return 1

    root_display, root_tokens = resolve_license(ver, system, name, overrides)

    print(f"version: {version}")
    print(f"license: {root_display}")
    print(f"homepage: {homepage(ver)}")

    licenses_seen: set[str] = set(root_tokens)
    count = 0
    deps_available = True

    deps = fetch(
        f"{API}/systems/{system}/packages/{enc(name)}/versions/{enc(version)}:dependencies"
    )
    print()
    if isinstance(deps, _NotFound):
        deps_available = False
        print("transitive dependencies: (unavailable on deps.dev)")
    elif deps is None:
        print(
            f"transitive lookup failed for {system}/{name}@{version}", file=sys.stderr
        )
        return 1
    else:
        print("transitive dependencies:")
        for node in deps.get("nodes") or []:
            if node.get("relation") == "SELF":
                continue
            count += 1
            vk = node["versionKey"]
            nsys = vk["system"].lower()
            nname = vk["name"]
            nver = vk["version"]
            nrel = node["relation"].lower()

            node_doc = fetch(
                f"{API}/systems/{nsys}/packages/{enc(nname)}/versions/{enc(nver)}"
            )
            doc_for_resolve = node_doc if isinstance(node_doc, dict) else None
            nlic_display, nlic_tokens = resolve_license(
                doc_for_resolve, nsys, nname, overrides
            )
            licenses_seen.update(nlic_tokens)
            print(f"  [{nrel}] {nname}@{nver} : {nlic_display}")

        if count == 0:
            print("  (none)")

    print()
    print("summary:")
    if deps_available:
        print(f"  transitive dep count: {count}")
        print(f"  licenses in tree: {', '.join(sorted(licenses_seen))}")
    else:
        print("  transitive dep count: N/A (graph unavailable)")
        print(
            f"  licenses in tree: {', '.join(sorted(licenses_seen))} (root only, transitive unavailable)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
