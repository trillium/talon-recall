#!/bin/bash
# sync_from_active.sh — Copy core recall files from the active Talon installation
# to this standalone project. Run from the standalone recall directory.
#
# Usage: .scripts/sync_from_active.sh   (run from the standalone recall directory)
#
# Files synced (active -> standalone):
#   recall.py, recall.talon, recall_overlay.py,
#   recall_combine_mode.talon, recall_overlay_keys.talon,
#   forbidden_recall_names.talon-list
#
# Files NOT synced (standalone-only):
#   recall_core.py, basic_keys.talon, dictation_bravely.talon,
#   dictation_ender.py, dictation_ender.talon-list, mode_indicator.py,
#   modes.talon, README.md, saved_windows.json
#
# recall_commands.talon-list is special: the sanitized version from
# .scripts/ is always copied in, so personal commands don't leak.

ACTIVE_DIR="$HOME/.talon/user/talon_community/plugin/recall"
STANDALONE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

SYNC_FILES=(
    recall.py
    recall.talon
    recall_overlay.py
    recall_combine_mode.talon
    recall_overlay_keys.talon
    forbidden_recall_names.talon-list
)

if [ ! -d "$ACTIVE_DIR" ]; then
    echo "Error: Active recall directory not found at $ACTIVE_DIR"
    exit 1
fi

changed=0
for file in "${SYNC_FILES[@]}"; do
    src="$ACTIVE_DIR/$file"
    dst="$STANDALONE_DIR/$file"

    if [ ! -f "$src" ]; then
        echo "  SKIP  $file (not in active)"
        continue
    fi

    if [ -f "$dst" ] && diff -q "$src" "$dst" > /dev/null 2>&1; then
        echo "  OK    $file (identical)"
    else
        cp "$src" "$dst"
        echo "  SYNC  $file"
        changed=$((changed + 1))
    fi
done

if [ "$changed" -eq 0 ]; then
    echo ""
    echo "Already in sync."
else
    echo ""
    echo "Synced $changed file(s)."
fi

# ── Sanitized commands list ──────────────────────────────────────────
# Always overwrite recall_commands.talon-list with the sanitized version
# so personal commands never ship in the standalone package.

SANITIZED="$STANDALONE_DIR/.scripts/recall_commands.sanitized.talon-list"
COMMANDS_DST="$STANDALONE_DIR/recall_commands.talon-list"

if [ -f "$SANITIZED" ]; then
    if [ -f "$COMMANDS_DST" ] && diff -q "$SANITIZED" "$COMMANDS_DST" > /dev/null 2>&1; then
        echo "  OK    recall_commands.talon-list (sanitized, identical)"
    else
        cp "$SANITIZED" "$COMMANDS_DST"
        echo "  SYNC  recall_commands.talon-list (sanitized)"
    fi
else
    echo "  SKIP  recall_commands.talon-list (no sanitized source in .scripts/)"
fi

# ── Dependency check ─────────────────────────────────────────────────
# Find actions.user.X() calls in synced .py files that aren't defined
# in either recall.py or recall_core.py (the standalone shim).

echo ""
echo "Checking dependencies..."

# Collect all actions.user.X calls from synced python files
calls=$(grep -ohP 'actions\.user\.\w+' "$STANDALONE_DIR/recall.py" "$STANDALONE_DIR/recall_overlay.py" 2>/dev/null \
    | sed 's/actions\.user\.//' | sort -u)

# Collect all action definitions from recall.py and recall_core.py
# Matches: "def action_name(" in action_class blocks
defs=$(grep -ohP 'def \w+\(' "$STANDALONE_DIR/recall.py" "$STANDALONE_DIR/recall_core.py" 2>/dev/null \
    | sed 's/def //; s/(//' | sort -u)

missing=0
for call in $calls; do
    if ! echo "$defs" | grep -qx "$call"; then
        echo "  MISSING  actions.user.$call — needs shim in recall_core.py"
        missing=$((missing + 1))
    fi
done

if [ "$missing" -eq 0 ]; then
    echo "All dependencies satisfied."
else
    echo ""
    echo "WARNING: $missing action(s) used but not defined in standalone."
    echo "Add shims to recall_core.py for the missing actions above."
    exit 1
fi
