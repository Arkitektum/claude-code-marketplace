---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
disable-model-invocation: true
---

First, check whether this repo is set up for domain docs: look in `CLAUDE.md` (or
`AGENTS.md`) for the `arkitektum-development:domain-docs` marker. If it is missing, tell
the user the repo has not been configured yet and offer to run the `/setup-domain-docs`
skill first so the glossary and decisions you write get read back in future sessions. If
the user declines, fall back to a root `CONTEXT.md` and `docs/adr/`.

Then run a `/grilling` session, using the `/domain-modeling` skill. Write the glossary and
decisions to the locations recorded in the domain-docs block (or the fallback defaults).
