# arkitektum-development

Development workflow skills for Claude Code. The headline skills run a relentless
interview to sharpen a plan before you build; one variant also records the resulting
glossary and decisions so they survive across sessions.

## Skills

Each skill is licensed independently. Check the license column before reusing content;
skills added later may ship under different terms.

| Skill                                    | Invocation   | Covers                                                              | License        | Source            |
|------------------------------------------|--------------|---------------------------------------------------------------------|----------------|-------------------|
| `/arkitektum-development:grill-me`          | slash only   | Relentless interview to sharpen a plan or design                    | MIT            | mattpocock/skills |
| `/arkitektum-development:grill-with-docs`   | slash only   | `grill-me` plus a glossary and decision records written as you go   | MIT (modified) | mattpocock/skills |
| `/arkitektum-development:setup-domain-docs` | slash only   | Wire a repo so domain docs are read back; record where they live    | MIT            | Arkitektum        |
| `grilling`                               | model/slash  | The interview engine used by the grill skills                       | MIT            | mattpocock/skills |
| `domain-modeling`                        | model/slash  | Build and maintain the glossary and decision records                | MIT (modified) | mattpocock/skills |

`grilling` and `domain-modeling` are auto-invocable: Claude may load them on relevant
prompts (for example "stress-test this plan") without an explicit slash command.

## How the pieces fit

`/arkitektum-development:grill-with-docs` runs `grilling` and `domain-modeling`. Before
writing anything it checks the repo's `CLAUDE.md` (or `AGENTS.md`) for an
`arkitektum-development:domain-docs` block; if it is missing it offers to run
`/arkitektum-development:setup-domain-docs` first. That setup skill records where the
glossary and decisions live, supporting standard `docs/adr/` markdown or an alternative the
project already uses such as Backlog.md.

## Attribution

`grill-me`, `grill-with-docs`, `grilling`, and `domain-modeling` are derived from
[mattpocock/skills](https://github.com/mattpocock/skills) at commit
`5d78bd0903420f97c791f834201e550c765699f8`. `grill-with-docs` and `domain-modeling` are
modified to read and write the doc locations recorded by `/setup-domain-docs` and to
support non-ADR decision systems. `setup-domain-docs` is authored by Arkitektum, inspired
by that repo's setup skill but scoped to domain docs only.

These four skills are licensed under the MIT License:

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
