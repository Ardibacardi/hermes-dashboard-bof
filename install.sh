#!/usr/bin/env bash
# Ad Miner Dashboard — Install script for Hermes Agent
# Copies plugin + theme to ~/.hermes/

set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
PLUGIN_DIR="$HERMES_HOME/plugins/ad-miner-dashboard"
THEME_DIR="$HERMES_HOME/dashboard-themes"

echo "═══ Ad Miner Dashboard Installer ═══"
echo ""

# --- Plugin ---
echo "📦 Installing plugin to $PLUGIN_DIR ..."
mkdir -p "$PLUGIN_DIR/dashboard/dist"
cp plugins/ad-miner-dashboard/dashboard/manifest.json "$PLUGIN_DIR/dashboard/"
cp plugins/ad-miner-dashboard/dashboard/plugin_api.py "$PLUGIN_DIR/dashboard/"
cp plugins/ad-miner-dashboard/dashboard/dist/index.js "$PLUGIN_DIR/dashboard/dist/"
cp plugins/ad-miner-dashboard/dashboard/dist/style.css "$PLUGIN_DIR/dashboard/dist/"
echo "   ✓ Plugin installed"

# --- Theme (optional) ---
if [ -f "themes/metabolae-ops.yaml" ]; then
  echo "🎨 Installing theme to $THEME_DIR ..."
  mkdir -p "$THEME_DIR"
  cp themes/metabolae-ops.yaml "$THEME_DIR/"
  echo "   ✓ Theme installed"
fi

# --- Trigger rescan ---
echo ""
echo "🔄 Triggering dashboard plugin rescan..."
curl -s -X POST http://127.0.0.1:9119/api/dashboard/plugins/rescan 2>/dev/null || echo "   (dashboard not running — will pick up on next start)"

echo ""
echo "═══ Done ═══"
echo ""
echo "Start the dashboard:  hermes dashboard"
echo "Open:                 http://127.0.0.1:9119"
echo "Look for:             'Ad Miner' tab in the sidebar"
