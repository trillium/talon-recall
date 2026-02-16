# Recall — Name Your Windows, Control Them by Voice

Recall lets you save specific windows and switch between them instantly by voice. Instead of "focus Chrome" bringing up a random Chrome window, you name the one you care about and speak its name to get it back.

```
"recall assign edgar"     → saves the focused window as "edgar"
"edgar"                   → switches to it instantly
"edgar hello world"       → switches and types "hello world"
"edgar 1"                 → switches and presses the 1 key
"edgar hello world bravely" → switches, types, and presses Enter
```

## Prerequisites

### Talon (beta)

Recall requires [Talon](https://talonvoice.com), a hands-free input system. You need the **beta** version, which includes the speech engine.

1. Download Talon from https://talonvoice.com
2. Install and launch it — you'll see a Talon icon in your system tray
3. **Get beta access** by joining the [Talon Slack](https://talonvoice.com/chat) and following the beta instructions

### Speech model

Talon beta ships with the **Conformer** speech model, which provides excellent accuracy out of the box. No additional model setup is required — Talon will prompt you to download it on first launch.

### No other packages required

Recall is fully self-contained. It includes everything you need to get started with voice control:

- Text dictation (speaking words that get typed)
- Number input (speaking numbers to press number keys)
- Mode switching (command, dictation, and mixed modes)
- A mode indicator (colored dot showing your current mode)
- Basic keyboard commands (enter, escape, backspace, arrows, etc.)

If you later install [talonhub/community](https://github.com/talonhub/community) (the standard Talon command set), Recall automatically detects it and uses community's richer implementations instead of its own built-in shims.

## Installation

Clone or download this repo into your Talon user directory:

```bash
# Linux
git clone https://github.com/trillium/talon-recall ~/.talon/user/recall

# macOS
git clone https://github.com/trillium/talon-recall ~/Library/Talon/user/recall
```

Talon will automatically load the package. You should see a small colored dot at the top-center of your screen — that's the mode indicator.

## Getting started

### Understanding modes

Talon has three main modes, shown by the indicator dot color:

| Mode | Dot color | What it does |
|------|-----------|-------------|
| **Command** | Blue | Interprets speech as commands ("undo", "recall assign edgar") |
| **Dictation** | Gold | Types everything you say as text |
| **Mixed** | Green | Both at once — commands work AND unrecognized speech gets typed |

**Mixed mode is recommended for recall.** It lets you speak commands like "edgar" to switch windows, and also dictate text like "edgar hello world" to type into them.

To switch modes, say:
- `"mixed mode"` — enables both command and dictation (recommended)
- `"command mode"` — commands only
- `"dictation mode"` — typing only

### Saving a window

Focus any window, then say:

```
"recall assign edgar"
```

This saves the window with the name "edgar". Pick short, distinctive names that are easy to say — names of people work well (edgar, velma, oscar).

### Switching to a window

Just say the name:

```
"edgar"
```

### Dictating into a window

Say the name followed by what you want to type:

```
"edgar hello world"
```

This switches to edgar's window and types "hello world".

### Dictating and pressing Enter

Add "bravely" at the end to press Enter after typing:

```
"edgar hello world bravely"
```

This is useful for chat apps, terminal commands, and anywhere you want to type and submit in one breath. The word "bravely" is configurable — edit `dictation_ender.talon-list` to change it.

### Pressing a number key

Say the name followed by a number:

```
"edgar 1"
```

This switches to the window and presses the number key. Useful for selecting numbered options in CLI tools.

## All commands

| Command | What it does |
|---------|-------------|
| `"recall assign <name>"` | Save the focused window |
| `"<name>"` | Switch to a saved window |
| `"<name> <dictation>"` | Dictate text into a window |
| `"<name> <dictation> bravely"` | Dictate + press Enter |
| `"<name> <number>"` | Press a number key |
| `"recall restore <name>"` | Relaunch a terminal at saved path |
| `"recall alias <name>"` | Add an alternate name (prompted) |
| `"recall combine <name>"` | Merge a duplicate entry (prompted) |
| `"recall rename <name>"` | Change a window's name (prompted) |
| `"recall promote <alias>"` | Make an alias the primary name |
| `"recall list"` | Flash name labels on all windows |
| `"recall help"` | Full-screen help panel |
| `"recall forget <name>"` | Remove a saved window |
| `"recall forget all"` | Clear everything |
| `"recall close"` | Dismiss any overlay |

### Basic keyboard commands

These are included so you can operate without talonhub/community:

| Command | Key |
|---------|-----|
| `"slap"` | Enter |
| `"escape"` | Escape |
| `"junk"` | Backspace |
| `"tabby"` | Tab |
| `"go up/down/left/right"` | Arrow keys |
| `"undo"` / `"redo"` | Ctrl+Z / Ctrl+Shift+Z |
| `"copy this"` / `"paste this"` / `"cut this"` | Clipboard |
| `"select all"` | Ctrl+A |

## Customization

### Forbidden names

Some words can't be used as window names because they conflict with commands. Edit `forbidden_recall_names.talon-list` to add or remove reserved words.

### Dictation ender

The word "bravely" triggers Enter after dictation. Edit `dictation_ender.talon-list` to change it or add alternatives.

### Mode indicator

The indicator dot can be customized in your Talon settings:

```
settings():
    user.mode_indicator_show = true
    user.mode_indicator_size = 30
    user.mode_indicator_x = 0.5
    user.mode_indicator_y = 0
    user.mode_indicator_color_alpha = 0.75
```

## How it works

Recall saves window references (ID, app name, title, terminal path) to `saved_windows.json` in the package directory. When you say a window's name, it finds the window by ID, focuses it, and updates the terminal path if applicable.

For terminals, recall detects the working directory by parsing the window title (e.g., `user@host: /path`) or reading `/proc/<pid>/cwd`. The `restore` command can relaunch a terminal at the saved path if the original was closed.

## Using with talonhub/community

If you install [talonhub/community](https://github.com/talonhub/community), recall automatically uses community's richer implementations for:

- Text dictation (with auto-capitalization and spacing)
- Number recognition (full range, not just 0-20)
- Window focusing (with timeout and error handling)
- Spoken form generation (smarter name matching)

The `basic_keys.talon` and `modes.talon` files in this package may conflict with community's versions. If you install community, you can safely delete those two files — community provides its own comprehensive key and mode commands.

## License

MIT
