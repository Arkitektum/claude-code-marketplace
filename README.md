# Claude Code Marketplace - Arkitektum

A collection of Claude Code plugins and skills maintained by Arkitektum. Plugins in this marketplace enforce organizational standards, security policies, and development conventions across all projects.

## Structure

```
.claude-plugin/
  marketplace.json          # Marketplace manifest listing all available plugins
plugins/
  arkitektum-mandatory/     # Mandatory plugin for all Arkitektum projects
    .claude-plugin/
      plugin.json           # Plugin metadata (name, version, description)
    hooks/
      hooks.json            # Hook definitions (SessionStart, PreToolUse, etc.)
    scripts/
      block-ide-config.sh       # Blocks Edit/Write to IDE config dirs
      block-ide-config-bash.sh  # Blocks Bash commands targeting IDE config files
    instructions.md         # Instructions injected at session start
```

## Plugins

### arkitektum-mandatory

Mandatory plugin applied to all Arkitektum projects. It does two things:

1. **Session instructions** -- Injects organizational policies on session start covering dependency management, license compliance, restricted tools/operations, and security practices. See [instructions.md](plugins/arkitektum-mandatory/instructions.md) for the full set of rules.

2. **IDE config protection** -- PreToolUse hooks that block Claude from modifying IDE configuration directories (`.vscode/`, `.idea/`, `.vs/`), preventing potential security issues from malicious auto-run configs.

### arkitektum-security

OWASP knowledge bases (web, LLM, MCP, agentic, CI/CD, infrastructure) for reviewing and remediating security risks. See [its README](plugins/arkitektum-security/README.md).

### mattpocock-skills

Selected skills from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT): `grill-me`, `grilling`, `grill-with-docs`, `domain-modeling`, `setup-matt-pocock-skills`, `handoff`, `teach`, `wait-what` and `writing-for-agents`.

The entry has no files in this repository. It fetches the upstream `skills/` directory and loads only the skills listed under `skills` in `marketplace.json`, so upstream hooks, MCP servers and unlisted skills don't come along. It has no `ref` and no `version`, so it tracks upstream `main` and every upstream commit is a new version.

- **Source URL**: keep the full `https://` URL. With the `owner/repo` shorthand, Claude Code clones over SSH first. The claude-docker firewall blocks SSH, and plugin updates don't fall back to HTTPS.
- **Adding a skill**: add its path under `skills`, plus any skill it refers to.
- **When upstream renames or removes a listed skill**: `/plugin` reports `Path not found` for that path. Update or remove the path.
- **Replaces `arkitektum-development`**: the `renames` entry moves `enabledPlugins` over. Outside claude-docker, run `/plugin install mattpocock-skills@arkitektum-marketplace` once, because Claude Code doesn't download a renamed plugin by itself.
- **Domain docs**: upstream writes the glossary to `GLOSSARY.md`, while the old `setup-domain-docs` pointed at `CONTEXT.md`. In a repo set up with the old skill, run `/mattpocock-skills:setup-matt-pocock-skills` once. It offers to rename the file.

## Usage

[claude-docker](https://github.com/Arkitektum/claude-docker) installs `arkitektum-mandatory` and `mattpocock-skills` and turns on auto-update for this marketplace. Outside it, add the marketplace and install from a Claude Code session:

```
/plugin marketplace add Arkitektum/claude-code-marketplace
/plugin install arkitektum-mandatory@arkitektum-marketplace
```

Then turn on auto-update under `/plugin` → **Marketplaces** → `arkitektum-marketplace` → **Enable auto-update**. Third-party marketplaces have it off by default.

To declare the marketplace and its plugins for everyone in a repository, commit this to the repository's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "arkitektum-marketplace": {
      "source": { "source": "github", "repo": "Arkitektum/claude-code-marketplace" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "arkitektum-mandatory@arkitektum-marketplace": true
  }
}
```

## Adding a new plugin

1. Create a directory under `plugins/` with your plugin name
2. Add `.claude-plugin/plugin.json` with metadata:
   ```json
   {
     "name": "my-plugin",
     "description": "What this plugin does"
   }
   ```
   Leave out `version`. Claude Code then versions the plugin by commit SHA, so every merge reaches users. A `version` keeps users on their copy until someone changes it.
3. Add hooks, scripts, and instructions as needed (see `arkitektum-mandatory` for reference)
4. Register the plugin in `.claude-plugin/marketplace.json`
