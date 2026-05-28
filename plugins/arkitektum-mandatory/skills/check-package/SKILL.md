---
name: check-package
description: Fetch the latest stable version and license for a third-party package, walk its transitive dependency graph, and print the union of licenses found. Use when you need to look up a package's current version, license, or full transitive dependency licenses for pypi, npm, cargo, nuget, or go. Reports findings only, no policy decisions.
---

# check-package

Looks up the latest stable version and license of a third-party package, walks the full transitive dependency graph, and reports a license per node plus a summary (count of transitive deps, union of licenses in the tree). Backed by the deps.dev v3 API (Google's cross-ecosystem package metadata service).

This skill is a pure lookup tool. It does not classify, filter, or recommend, callers decide what to do with the output.

## How to invoke

```bash
${CLAUDE_PLUGIN_ROOT}/skills/check-package/check-package.py <ecosystem> <name>
```

| Ecosystem | Name format | Example |
|-----------|-------------|---------|
| `pypi`    | distribution name on PyPI            | `pypi requests` |
| `npm`     | package name (scoped names supported) | `npm @tanstack/react-query` |
| `cargo`   | crate name                            | `cargo serde` |
| `nuget`   | NuGet package id                      | `nuget Newtonsoft.Json` |
| `go`      | full module path                      | `go github.com/gorilla/mux` |

The transitive walk always runs. For packages with large dep graphs (hundreds of nodes) the call can take 30 to 60 seconds.

## Output

The first three lines describe the root package:

```
version: <latest stable version>
license: <SPDX expression or UNKNOWN>
homepage: <url or empty>
```

Then one line per transitive node, with the relation (`direct` or `indirect`), name, version, and license:

```
transitive dependencies:
  [direct] foo@1.2.3 : MIT
  [indirect] bar@2.0.0 : Apache-2.0
  ...
```

A summary block ends the output:

```
summary:
  transitive dep count: <integer>
  licenses in tree: <comma-separated union of SPDX expressions, including the root>
```

A license followed by `(override)` means the skill substituted a curated SPDX value because the upstream metadata was unparseable or missing.

## Handling `non-standard` and `UNKNOWN` entries

These markers mean deps.dev could not extract a valid SPDX identifier. The actual license usually exists upstream, deps.dev just couldn't read it.

### MANDATORY: always resolve via live fetch

Every `non-standard` and `UNKNOWN` entry (that is not already corrected by `(override)`) MUST be resolved by fetching the upstream `LICENSE` file live. This applies on every invocation, no exceptions.

- Do NOT answer from training data, memory, or prior conversation context.
- Do NOT assume "I know what license X uses" — licenses change (relicensing to BUSL/SSPL/AGPL, dual-license additions, fork divergence). A stale answer is worse than no answer.
- The resolution output MUST contain both (a) the SPDX identifier observed in the fetched file, and (b) the exact URL the content was read from. If either is missing, the entry is unresolved.

### Procedure

1. Count the entries that are `non-standard` or `UNKNOWN` and not already `(override)`-corrected.
2. **If 5 or fewer**: spawn one subagent (e.g., the `general-purpose` agent) per package. Each subagent fetches the package's source repository or registry page, reads the live `LICENSE` file, and returns `SPDX-identifier + source URL` per the mandatory rule above.
3. **If more than 5**: stop. Show the user the list of packages needing research and ask how to proceed (e.g., bulk-research via agent, or drop the dependency under review).

## Edge cases

- **Network failure / 404**: the script exits non-zero with a `lookup failed` message. Verify the package name and ecosystem. deps.dev occasionally lags new releases by minutes to hours.
- **Prereleases**: deps.dev's default version excludes prereleases for all five ecosystems. If a prerelease is needed, query the registry directly instead.
- **Unknown licenses**: nodes without license metadata report `UNKNOWN`, and `UNKNOWN` appears in the summary's union set when present.
- **Per-node lookups**: each transitive node triggers a separate HTTP call. The script is sequential by design, parallelism can be added if speed becomes a problem.
