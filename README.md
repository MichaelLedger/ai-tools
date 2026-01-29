# AI Tools

A collection of AI tool configurations and integrations for development workflows.

## Features

- **Figma MCP Integration** - Connect Cursor IDE to Figma for design-to-code workflows
- **MCP Server Configurations** - Pre-configured Model Context Protocol servers

## Getting Started

### Figma MCP Setup

The Figma MCP allows Cursor's AI to directly access your Figma designs, fetch layout data, and download assets.

1. Get a [Figma Personal Access Token](https://www.figma.com/developers/api#access-tokens)
2. Update `.cursor/mcp.json` with your API key
3. Restart Cursor IDE

See [docs/figma-mcp-setup.md](docs/figma-mcp-setup.md) for detailed setup instructions.

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/ai-tools.git
cd ai-tools

# Copy and configure MCP settings
cp .cursor/mcp.json ~/.cursor/mcp.json
# Edit ~/.cursor/mcp.json and add your Figma API key
```

## Project Structure

```
ai-tools/
├── .cursor/
│   ├── mcp.json              # MCP server configuration template
│   └── rules/
│       └── figma-mcp.mdc     # Figma MCP usage guidelines
├── docs/
│   └── figma-mcp-setup.md    # Detailed setup documentation
├── LICENSE
└── README.md
```

## Available MCP Integrations

| Integration | Description | Status |
|-------------|-------------|--------|
| Figma MCP | Design-to-code with Figma | ✅ Ready |

## Usage

Once configured, you can use Figma MCP in Cursor by:

1. Opening Agent mode (Cmd/Ctrl + I)
2. Sharing a Figma URL
3. Asking the AI to convert the design to code

**Example prompts:**
- "Get the design data from [Figma URL]"
- "Convert this Figma design to React components"
- "Download the icons from [Figma URL] to src/assets"

## Security

⚠️ **Important:** Never commit API keys to version control.

- The `.cursor/mcp.json` template uses a placeholder for the API key
- For production use, configure your API key in `~/.cursor/mcp.json` (global)
- Consider using environment variables for sensitive data

## License

See [LICENSE](LICENSE) for details.
