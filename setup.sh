#!/bin/bash
# Setup script for claude-stock-tools
# Installs the stock-analysis skill and filing-downloader MCP server

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Claude Stock Tools Setup ==="

# 1. Install Python venv and dependencies
echo ""
echo "[1/4] Setting up Python environment..."
cd "$SCRIPT_DIR/mcp"
if [ ! -d ".venv" ]; then
    python3.13 -m venv .venv
fi
.venv/bin/pip install -e . -q
echo "  Done. Python deps installed in mcp/.venv/"

# 2. Create skill symlink
echo ""
echo "[2/4] Installing stock-analysis skill..."
SKILL_DIR="$HOME/.claude/skills/stock-analysis"
if [ -L "$SKILL_DIR" ]; then
    echo "  Symlink already exists, updating..."
    rm "$SKILL_DIR"
elif [ -d "$SKILL_DIR" ]; then
    echo "  Backing up existing skill directory..."
    mv "$SKILL_DIR" "${SKILL_DIR}.bak.$(date +%s)"
fi
mkdir -p "$HOME/.claude/skills"
ln -s "$SCRIPT_DIR/skill" "$SKILL_DIR"
echo "  Symlinked: $SKILL_DIR -> $SCRIPT_DIR/skill"

# 3. Register MCP server
echo ""
echo "[3/4] Registering filing-downloader MCP server..."
MCP_CMD="$SCRIPT_DIR/mcp/.venv/bin/python"
claude mcp remove filing-downloader -s user 2>/dev/null || true
claude mcp add --scope user filing-downloader -- "$MCP_CMD" -m filing_downloader.server
echo "  MCP server registered (user scope)"

# 4. Verify
echo ""
echo "[4/4] Verification..."
echo "  Skill:  $(ls -la "$SKILL_DIR" | grep -o '-> .*')"
echo "  MCP:    $(claude mcp get filing-downloader 2>&1 | head -3)"

echo ""
echo "=== Setup complete ==="
echo "Restart Claude Code to use the new tools."
echo ""
echo "Usage examples:"
echo '  分析一下02313'
echo '  600519估值'
