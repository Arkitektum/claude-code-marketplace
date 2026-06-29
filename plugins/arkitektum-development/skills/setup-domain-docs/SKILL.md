---
name: setup-domain-docs
description: Configure this repo so domain docs (a glossary and decision records) written by grill-with-docs are read back in future sessions. Detects existing decision/ADR systems (docs/adr, Backlog.md, or other) and records where docs live. Run once per repo, or when grill-with-docs hands off to it.
---

# Set up domain docs

Wire this repo so the glossary and decisions that `/grill-with-docs` and `/domain-modeling`
produce are both written to the right place and read back automatically in later sessions.

The mechanism is a short "Domain docs" section in the repo's agent instructions
(`CLAUDE.md` or `AGENTS.md`). It tells every future session to read the glossary and
decisions before working, and records where those live. Without it, the docs are
write-only.

This is a prompt-driven skill, not a script. Explore, present what you found, confirm with
the user, then write.

## 1. Explore

Read the repo to learn its starting state. Do not assume:

- `CLAUDE.md` and `AGENTS.md` at the root. Which exists? Does either already describe
  where the glossary and decisions live (a domain-docs habit, under any heading)?
- `CONTEXT.md` and `CONTEXT-MAP.md` at the root (existing glossary, single- or multi-context).
- Decision systems already in use:
  - `docs/adr/` (standard markdown ADRs)
  - Backlog.md (a `backlog/` directory or its config; it may also be exposed as the
    `backlog` MCP server)
  - Anything else the repo uses to record decisions.

## 2. Ask, one at a time

Assume the user may not know these terms. Start each section with a one-line explainer,
then present the choices and the detected default. Ask one section, wait for the answer,
then move on.

**A. Glossary location.** Where the project's ubiquitous language lives.
- Default: a single `CONTEXT.md` at the root.
- Multi-context repos (typically monorepos): a `CONTEXT-MAP.md` at the root pointing to
  per-context `CONTEXT.md` files.

**B. Decisions location.** Where architectural decisions get recorded. Default to whatever
you detected:
- `docs/adr/` markdown (sequential `0001-slug.md`).
- Backlog.md, decisions recorded as items in the project's Backlog.md.
- Other, the user describes the system in a sentence; record it as freeform prose.

## 3. Confirm, then write

Show the user the exact block you will add, and let them edit it before writing.

Pick the file to edit:
- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which to create. Do not pick for them. Never create one
  when the other already exists.

If the file already describes where domain docs live, update that section in place rather
than appending a duplicate. Do not touch the surrounding content.

The section (fill the locations from the answers):

```markdown
## Domain docs

Before working, read these for the project's vocabulary and prior decisions, and keep your
own naming consistent with the glossary:

- Glossary: `CONTEXT.md`
- Decisions: `docs/adr/`

If your work would contradict a recorded decision, surface that rather than silently
overriding it. New glossary terms and decision records are created by `/grill-with-docs`
(and the `domain-modeling` skill it uses), which own the format and numbering; do not
hand-roll your own.
```

This section is for *consuming* the docs. Authoring, the ADR format, numbering, and when a
decision is worth recording, lives in the `domain-modeling` skill, not here.

## 4. Done

Tell the user setup is complete and that `/grill-with-docs` and `/domain-modeling` will now
read and write the locations recorded in this section. Mention they can edit it directly
later; re-run this skill only to change where docs live.
