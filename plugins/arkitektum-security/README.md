# arkitektum-security

Security skills for Claude Code. Each skill is invocable as a slash command (for example
`/arkitektum-security:owasp-llm`) and is also auto-loaded by Claude when a relevant
security question comes up. The skills encode the OWASP "Top N" risk catalogues as
structured reference documents an agent can query to identify, assess, and remediate
risks.

## Skills

Each skill is licensed independently. Check the license column before reusing content;
skills added later may ship under different terms.

| Skill                                  | Covers                                | License      | Source                        |
|----------------------------------------|---------------------------------------|--------------|-------------------------------|
| `/arkitektum-security:owasp-top-10`         | OWASP Top 10 for Web Apps (2025)      | CC-BY-SA-4.0 | OWASP, via microsoft/hve-core |
| `/arkitektum-security:owasp-llm`            | OWASP Top 10 for LLM Apps (2025)      | CC-BY-SA-4.0 | OWASP, via microsoft/hve-core |
| `/arkitektum-security:owasp-agentic`        | OWASP Top 10 for Agentic Apps (2026)  | CC-BY-SA-4.0 | OWASP, via microsoft/hve-core |
| `/arkitektum-security:owasp-mcp`            | OWASP MCP Top 10 (2025)               | CC-BY-SA-4.0 | OWASP, via microsoft/hve-core |
| `/arkitektum-security:owasp-infrastructure` | OWASP Infrastructure Top 10 (2024)    | CC-BY-SA-4.0 | OWASP, via microsoft/hve-core |
| `/arkitektum-security:owasp-cicd`           | OWASP CI/CD Top 10                     | CC-BY-SA-4.0 | OWASP, via microsoft/hve-core |

## What this is, and where it comes from

These skills are a **verbatim copy** of the OWASP security skills from
[microsoft/hve-core](https://github.com/microsoft/hve-core), taken at commit
`88dc7f2922bbe1fb11b775b2d4a2c82b56ad40d3`. The provenance has three layers:

1. **OWASP** publishes the underlying risk catalogues (the "Top N" lists, category
   names, and identifiers) under CC BY-SA 4.0.
2. **hve-core** restructured those catalogues into agent-consumable reference documents
   and *added its own detection and remediation guidance*. That added prose is hve-core's
   authored interpretation, not OWASP text, and is not OWASP-endorsed.
3. **This plugin** copies hve-core's reference documents unchanged and only adjusts each
   `SKILL.md` frontmatter so the skill is invocable as a slash command. We add nothing to
   the reference content and do not maintain it.

Two consequences worth knowing:

- The reference content is a **point-in-time snapshot**. OWASP's catalogues are living
  documents; category names and identifiers in these files may lag the current published
  versions. Treat them as hve-core's snapshot, not as the authoritative OWASP text.
- Accuracy of the detection/remediation guidance rests on hve-core, not OWASP.

## Attribution and licensing

The OWASP-derived content is licensed under CC BY-SA 4.0
(https://creativecommons.org/licenses/by-sa/4.0/). hve-core itself is MIT. Each skill's
`SKILL.md` carries a `## Third-Party Attribution` block naming the OWASP source, the
CC BY-SA 4.0 license, and the modifications. Some reference documents additionally carry a
per-document OWASP attribution footer inherited from upstream; where a reference document
has none, the skill-level attribution in its `SKILL.md` governs.

Because the OWASP-derived content carries CC BY-SA 4.0 (ShareAlike), any redistributed
version of it must remain under CC BY-SA 4.0. This does not affect the rest of the plugin.

OWASP® is a registered trademark of the OWASP Foundation. Use does not imply endorsement.
