# AI Tools

A backup and shareable export of Cursor IDE customizations — MCP servers, plugins, rules, skills, hooks, slash commands, and subagents — plus project-level templates for Figma MCP.

The canonical copy lives in [`cursor/customize/`](cursor/customize/). Files there are symlinked into `~/.cursor/` on the machine where they were authored, so edits in the repo propagate to the live config automatically.

## What's included

| Category | Location | Highlights |
|----------|----------|------------|
| **MCP servers** | [`cursor/customize/MCPs/`](cursor/customize/MCPs/) | `xcode-tools` (Apple Xcode MCP), Framelink Figma MCP, GitHub |
| **Plugins** | [`cursor/customize/Plugins/`](cursor/customize/Plugins/) | Figma, GitHub, Atlassian, Superpowers (metadata + plugin MCP configs) |
| **Rules** | [`cursor/customize/Rules/`](cursor/customize/Rules/) | Swift concurrency & memory, Figma MCP, file copyright header |
| **Skills** | [`cursor/customize/Skills/`](cursor/customize/Skills/) | iOS conventions, graphify, generate-similar-photos, kekenet-friends-lesson |
| **Hooks** | [`cursor/customize/Hooks/`](cursor/customize/Hooks/) | `afterFileEdit` → swiftformat on `.swift` files |
| **Commands** | [`cursor/customize/Commands/`](cursor/customize/Commands/) | `/build`, `/test` (Xcode MCP) |
| **Subagents** | [`cursor/customize/Subagents/`](cursor/customize/Subagents/) | `swift-reviewer` |
| **Recommendations** | [`cursor/customize/RECOMMENDATIONS.md`](cursor/customize/RECOMMENDATIONS.md) | Curated pick list for senior iOS engineers |

Each category has an `installed.json` manifest describing what is configured and where it links.

## Project structure

```
ai-tools/
├── cursor/customize/          # Full Cursor customization export (source of truth)
│   ├── MCPs/mcp.json
│   ├── Plugins/
│   ├── Rules/
│   ├── Skills/
│   ├── Hooks/
│   ├── Commands/
│   ├── Subagents/
│   └── RECOMMENDATIONS.md
├── .cursor/
│   ├── mcp.json               # Minimal project-level MCP template (Figma only)
│   └── rules/
│       └── figma-mcp.mdc
├── docs/
│   └── figma-mcp-setup.md
├── LICENSE
└── README.md
```

## Install

### Prerequisites

- **Xcode 26.3+** with **Xcode Tools MCP** enabled (Xcode → Settings → Intelligence)
- **swiftformat** on `PATH` (for the edit hook)
- **Figma Personal Access Token** if using Framelink Figma MCP
- **GitHub PAT** via env var if using the GitHub plugin (`GITHUB_PERSONAL_ACCESS_TOKEN`)

### Restore to `~/.cursor/`

From the repo root, symlink the customize tree into your user Cursor config:

```bash
REPO="$(pwd)/cursor/customize"
C="$HOME/.cursor"

mkdir -p "$C/rules" "$C/agents" "$C/commands" "$C/skills" "$C/hooks"

# MCP (edit machine-specific paths first — see Security below)
cp "$REPO/MCPs/mcp.json" "$C/mcp.json"

# Rules, subagents, commands, skills
ln -sfn "$REPO/Rules/swift-concurrency.mdc"  "$C/rules/swift-concurrency.mdc"
ln -sfn "$REPO/Rules/swift-memory.mdc"       "$C/rules/swift-memory.mdc"
ln -sfn "$REPO/Subagents/swift-reviewer.md"  "$C/agents/swift-reviewer.md"
ln -sfn "$REPO/Commands/build.md"            "$C/commands/build.md"
ln -sfn "$REPO/Commands/test.md"             "$C/commands/test.md"
ln -sfn "$REPO/Skills/ios-swift-conventions" "$C/skills/ios-swift-conventions"

# Hooks
chmod +x "$REPO/Hooks/scripts/swiftformat-edit.sh"
ln -sfn "$REPO/Hooks/scripts/swiftformat-edit.sh" "$C/hooks/swiftformat-edit.sh"
ln -sfn "$REPO/Hooks/hooks.json"                 "$C/hooks.json"
```

Then edit `~/.cursor/mcp.json`:

1. Replace `YOUR_FIGMA_API_KEY` with your [Figma token](https://www.figma.com/developers/api#access-tokens)
2. Update the `github` command path if it does not match your machine
3. Restart Cursor

### Per-project Figma MCP

For a single repo, copy the minimal template instead:

```bash
cp .cursor/mcp.json /path/to/your-project/.cursor/mcp.json
# Edit and add your Figma API key
```

See [docs/figma-mcp-setup.md](docs/figma-mcp-setup.md) for detailed Figma setup.

## Usage

### iOS workflow

| Action | How |
|--------|-----|
| Build active scheme | `/build` slash command (requires Xcode open + xcode-tools MCP) |
| Run tests | `/test` slash command |
| Review Swift changes | Invoke the `swift-reviewer` subagent |
| Auto-format agent edits | Runs via `afterFileEdit` hook (swiftformat) |
| Swift rules | Load automatically on `**/*.swift` files |

Fill in the `TODO` sections in [`Skills/ios-swift-conventions/SKILL.md`](cursor/customize/Skills/ios-swift-conventions/SKILL.md) with your team's real module layout, logging, and test conventions.

### Figma workflow

1. Open Agent mode (Cmd+I)
2. Share a Figma URL
3. Ask the agent to fetch design context or convert to code

Example prompts:

- "Get the design data from [Figma URL]"
- "Convert this Figma design to SwiftUI"
- "Download the icons from [Figma URL]"

## MCP servers

| Server | Auth | Notes |
|--------|------|-------|
| `xcode-tools` | Xcode permission prompt | `xcrun mcpbridge` — build, test, diagnostics, SwiftUI previews |
| `Framelink Figma MCP` | API key in `mcp.json` | Read/export Figma files via npx |
| `github` | Local start script | Machine-specific path; configure per install |
| Figma plugin | OAuth | Installed via Cursor marketplace — no key in config |
| GitHub plugin | `GITHUB_PERSONAL_ACCESS_TOKEN` env var | Installed via Cursor marketplace |
| Atlassian plugin | OAuth | Jira/Confluence — no Docker token needed |

Removed from the live config (superseded or redundant): `swift-version-server`, `figma-2`, Docker `mcp-atlassian`.

## Security

**Never commit real API keys, tokens, or passwords.**

- `cursor/customize/MCPs/mcp.json` uses placeholders (`YOUR_FIGMA_API_KEY`) — verified clean of personal tokens
- Plugin MCP configs reference env vars (`${GITHUB_PERSONAL_ACCESS_TOKEN}`) or OAuth — no embedded secrets
- Skills that need keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`) read from environment or `.env` at runtime
- `.env` files are gitignored

Before sharing or pushing, scan for secrets:

```bash
rg -i 'figd_|ATATT|ghp_|sk-[a-zA-Z0-9]{20,}|api[_-]?key\s*=' cursor/customize/
```

**Machine-specific paths** (`/Users/...`) appear in some skill scripts and the GitHub MCP entry. Sanitize these if publishing publicly.

The kekenet skill script contains hardcoded third-party AES constants for Kekenet's public API — not your credentials, but worth keeping in a private repo if you open-source this project.

## License

See [LICENSE](LICENSE) for details.
