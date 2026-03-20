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

## Usage

To install a plugin from this marketplace in a project, add a reference in the project's `.claude/settings.json`:

```json
{
  "plugins": [
    "https://raw.githubusercontent.com/<org>/claude-code-marketplace/main/plugins/arkitektum-mandatory"
  ]
}
```

## Adding a new plugin

1. Create a directory under `plugins/` with your plugin name
2. Add `.claude-plugin/plugin.json` with metadata:
   ```json
   {
     "name": "my-plugin",
     "version": "1.0.0",
     "description": "What this plugin does"
   }
   ```
3. Add hooks, scripts, and instructions as needed (see `arkitektum-mandatory` for reference)
4. Register the plugin in `.claude-plugin/marketplace.json`
