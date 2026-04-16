#!/usr/bin/env bash
set -e

if [ -z "$1" ]; then
  echo "Usage: ./install.sh <path_to_agent_project_root>"
  echo "Example: ./install.sh ../my-cool-agent"
  exit 1
fi

DEST="$1/.agents/skills/trino-query"
echo "Installing Trino Query skill plugin to $DEST..."

mkdir -p "$DEST"
cp -r trino-query/* "$DEST/"
# Also try copying the venv if we want? No, let's let the user install it locally

echo "✅ Trino Query Skill installed successfully into $DEST!"
echo ""
echo "Next Steps in your target project:"
echo "1. Change directory to the newly installed skill:"
echo "   cd $DEST"
echo "2. Create your configuration:"
echo "   cp .env.example .env"
echo "3. Update your credentials inside $DEST/.env"
echo ""
echo "Note: The Python environment and dependencies will be set up automatically on the first run."
echo ""
echo "Now start up your Agent/Claude Code at your project root and try asking about your Data Lakehouse!"
echo "Example: 'Show me all catalogs available in Trino'"
