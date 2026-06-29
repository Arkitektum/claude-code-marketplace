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

## Attribution

The skills above contain content from works by the OWASP Foundation, licensed under
CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). The content has been
restructured into agent-consumable reference format with added detection and
remediation guidance, and the skill frontmatter was adjusted to make each skill
invocable as a slash command. Adapted from
[microsoft/hve-core](https://github.com/microsoft/hve-core) at commit
`88dc7f2922bbe1fb11b775b2d4a2c82b56ad40d3` (MIT). Per-document attribution is retained
in each reference file.

Because these skills carry CC BY-SA 4.0 (ShareAlike), redistributed versions of the
OWASP-derived content must remain under CC BY-SA 4.0. This does not affect the rest of
the plugin.

OWASP® is a registered trademark of the OWASP Foundation. Use does not imply endorsement.
