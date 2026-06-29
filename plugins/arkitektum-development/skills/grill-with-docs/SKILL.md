---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
disable-model-invocation: true
---

First, check whether this repo is set up for domain docs: read `CLAUDE.md` (or
`AGENTS.md`) and judge whether it already says where the glossary and decisions live. If
it does not, stop and let the user decide before grilling. Explain briefly:

- Why it matters: the glossary and decisions you are about to write are only useful if
  future sessions read them, which means the repo's agent instructions must point at them.
- What setup does: `/setup-domain-docs` asks where the glossary and decisions should live
  (detecting any system already in use, `docs/adr/`, Backlog.md, or other) and adds a
  short "Domain docs" section to `CLAUDE.md`/`AGENTS.md`, with your confirmation.

Offer to run `/setup-domain-docs` first (recommended). If the user declines, fall back to
a root `CONTEXT.md` and `docs/adr/` for this session.

Then run a `/grilling` session, using the `/domain-modeling` skill. Write the glossary and
decisions to the locations the instructions name (or the fallback defaults).
