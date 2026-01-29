# Figma MCP Setup Guide for Cursor

This guide explains how to set up and use the Framelink Figma MCP (Model Context Protocol) integration with Cursor IDE.

## What is Figma MCP?

Figma MCP allows Cursor's AI to directly access Figma design files, fetch layout information, extract styles, and download assets. This enables seamless design-to-code workflows.

## Prerequisites

1. **Cursor IDE** (latest version)
2. **Node.js** (v18 or later)
3. **Figma Account** with API access
4. **Figma Personal Access Token**

## Getting Your Figma API Key

1. Log in to [Figma](https://www.figma.com)
2. Go to **Settings** → **Account**
3. Scroll to **Personal access tokens**
4. Click **Generate new token**
5. Give it a descriptive name (e.g., "Cursor MCP")
6. Copy the token (it won't be shown again!)

## Installation

### Option 1: Global Configuration (Recommended)

Add the Figma MCP to your global Cursor settings:

1. Open or create `~/.cursor/mcp.json`
2. Add the following configuration:

```json
{
  "mcpServers": {
    "Framelink Figma MCP": {
      "command": "npx",
      "args": [
        "-y",
        "figma-developer-mcp",
        "--figma-api-key=YOUR_FIGMA_API_KEY",
        "--stdio"
      ]
    }
  }
}
```

3. Replace `YOUR_FIGMA_API_KEY` with your actual Figma personal access token

### Option 2: Project-Level Configuration

For project-specific setup, create `.cursor/mcp.json` in your project root with the same configuration.

### Option 3: Using Environment Variables (Most Secure)

1. Set the environment variable:
   ```bash
   export FIGMA_API_KEY="your_figma_api_key_here"
   ```

2. Reference it in your mcp.json:
   ```json
   {
     "mcpServers": {
       "Framelink Figma MCP": {
         "command": "npx",
         "args": [
           "-y",
           "figma-developer-mcp",
           "--figma-api-key=${FIGMA_API_KEY}",
           "--stdio"
         ]
       }
     }
   }
   ```

## Verifying the Setup

1. Restart Cursor IDE
2. Open Agent mode (Cmd/Ctrl + I)
3. The Figma MCP should appear in the available tools
4. Try asking: "Get the design data from [your Figma URL]"

## Available Commands

### Get Figma Data

Fetches design structure, styles, and component information from a Figma file.

**Usage:**
```
Get the design from https://www.figma.com/file/ABC123/MyDesign
```

**What it returns:**
- Layout hierarchy
- Component structure
- Styles (colors, typography, spacing)
- Auto-layout settings
- Constraints and positioning

### Download Figma Images

Downloads images, icons, and illustrations from a Figma file as PNG or SVG.

**Usage:**
```
Download the icons from the Figma file to /path/to/assets
```

## Example Workflow

1. **Share your Figma URL:**
   ```
   Convert this Figma design to React: https://www.figma.com/file/ABC123/Homepage
   ```

2. **The AI will:**
   - Fetch the design data
   - Analyze the layout structure
   - Extract colors, fonts, and spacing
   - Generate corresponding code

3. **For images:**
   ```
   Download all the icons from the Figma file to src/assets/icons
   ```

## Troubleshooting

### MCP Not Showing Up

1. Ensure `mcp.json` is valid JSON
2. Restart Cursor IDE
3. Check Cursor's output panel for errors

### API Key Errors

1. Verify your token is correct
2. Ensure the token hasn't expired
3. Check you have access to the Figma file

### Rate Limiting

The Figma API has rate limits. If you hit them:
- Wait a few minutes before retrying
- Avoid fetching the entire file repeatedly
- Use specific node IDs when possible

## Security Best Practices

1. **Never commit API keys** to version control
2. Add `mcp.json` to `.gitignore` if it contains secrets
3. Use environment variables for sensitive data
4. Rotate your Figma tokens periodically

## Resources

- [Figma API Documentation](https://www.figma.com/developers/api)
- [Cursor MCP Documentation](https://docs.cursor.com/context/model-context-protocol)
- [figma-developer-mcp npm package](https://www.npmjs.com/package/figma-developer-mcp)

## File Structure

```
your-project/
├── .cursor/
│   ├── mcp.json           # MCP server configuration
│   └── rules/
│       └── figma-mcp.mdc  # Figma MCP usage rules
├── docs/
│   └── figma-mcp-setup.md # This setup guide
└── ...
```
