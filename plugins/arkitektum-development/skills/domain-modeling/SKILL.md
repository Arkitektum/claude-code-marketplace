---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## Where docs live

Read `CLAUDE.md` (or `AGENTS.md`) and use the glossary and decisions locations it names.
The instructions also indicate the decisions system: standard `docs/adr/` markdown, or an
alternative the project already uses (for example Backlog.md).

If the instructions say nothing about domain docs, stop and let the user decide, do not
silently default. Explain briefly, in two parts:

- Why it matters: the glossary (`CONTEXT.md`) is the project's shared vocabulary and the
  decision records capture why hard-to-reverse choices were made; for these to pay off,
  the repo's agent instructions must point future sessions at them, otherwise anything
  written here is never read back.
- What setup does: `/setup-domain-docs` asks where the glossary and decisions should live
  (detecting any system already in use, `docs/adr/`, Backlog.md, or other) and adds a
  short "Domain docs" section to `CLAUDE.md`/`AGENTS.md` so future sessions read them. It
  takes a moment and writes nothing without your confirmation.

Then offer the choice:

- Run `/setup-domain-docs` now (recommended).
- Proceed for this session with the defaults below (`CONTEXT.md` + `docs/adr/`), accepting
  that future sessions will not be told to read them.

Wait for the user's answer before writing anything.

## File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR.

Record the decision in the system named in the instructions. For `docs/adr/`, use
the format in [ADR-FORMAT.md](./ADR-FORMAT.md). For an alternative system (for example
Backlog.md), create the decision in that system following its own conventions and keep
the content to the same essentials: what was decided and why.
