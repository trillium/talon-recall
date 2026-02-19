# Recall — Name Your Windows, Control Them by Voice

Recall lets you save specific windows and switch between them instantly by voice. Keeping track of which window has which conversation gets pretty hard mentally when you're juggling a lot of agent coding windows. Naming them is a lot easier and lets you interact with windows more naturally, with less mental friction.

Give a specific window a specific name — for example, I use "mary" for my massage therapy booking application (they both start with MA, it works for my brain). Whenever I want to discuss features related to that project, I just start my sentence with the name:

```
"recall assign mary"        → saves the focused window as "mary"
"mary"                      → switches to it instantly
"mary what is the status?"  → switches and types the question
"mary 1"                    → switches and presses the 1 key
"mary commit and push bravely" → switches, types, and presses Enter
```

## Branches

| Branch | Who it's for | What's included |
|--------|-------------|-----------------|
| **`main`** | Talon users with [talonhub/community](https://github.com/talonhub/community) already installed | Just the recall plugin — relies on community for dictation, keys, formatting, etc. |
| **`standalone`** | New to Talon Voice, no existing setup | Everything bundled — recall plus all the community dependencies needed to get started from scratch |

If you already use Talon, use `main`. If you're new to Talon and want to try voice control with minimal setup, use `standalone`.

## Table of contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Getting started](#getting-started)
- [All commands](#all-commands)
- [Terminal path tracking](#terminal-path-tracking)
- [Customization](#customization)
- [How it works](#how-it-works)
- [Using with talonhub/community](#using-with-talonhubcommunity)

### Saving a window highlights it with a border and name label

![recall assign](images/recall_assign.png)

### "recall list" shows labels on all saved windows

![recall list](images/recall_list.png)

### "recall help" shows a full dashboard with all windows and commands

![recall help](images/recall_help.png)

## Prerequisites

### Talon (beta)

Recall requires [Talon](https://talonvoice.com), a hands-free input system. You need the **beta** version, which includes the Conformer speech engine needed for accurate voice recognition.

Talon has a free public version, but the beta provides the Conformer speech model that makes voice control practical. To get beta access:

1. **Download Talon** from [talonvoice.com](https://talonvoice.com) (available for Linux, macOS, and Windows)
2. **Subscribe to the Talon Beta tier** ($25/month) on [Patreon](https://www.patreon.com/join/lunixbochs) — this gets you beta builds, the Conformer speech model, and priority support. There's also a $5/month VIP tier for Slack access only, and a $100/month Professional tier for those who depend on Talon for work.
3. **Join the [Talon Slack](https://talonvoice.com/chat)** and message @aegis to link your Patreon — this unlocks beta downloads
4. **Install the beta** and launch it — you'll see a Talon icon in your system tray
5. **Download the speech model** — click the Talon tray icon and select `Speech Recognition → Conformer D`. See the [Talon installation guide](https://talon.wiki/Resource%20Hub/Talon%20Installation/installation_guide/) for detailed instructions.

The [Talon Slack](https://talonvoice.com/chat) community is also an excellent resource for getting help with setup.

### No other packages required

Recall is fully self-contained. It includes everything you need to get started with voice control:

- Text dictation (speaking words that get typed)
- Number input (speaking numbers to press number keys)
- Mode switching (command, dictation, and mixed modes)
- A mode indicator (colored dot showing your current mode)
- Basic keyboard commands (escape, backspace, arrows, etc.)
- **Ender words** — say "bravely" to press Enter after dictation, or by itself to just press Enter

If you later install [talonhub/community](https://github.com/talonhub/community) (the standard Talon command set), Recall automatically detects it and uses community's richer implementations instead of its own built-in shims.

## Installation

Clone or download this repo into your Talon user directory:

```bash
# macOS / Linux
git clone https://github.com/trillium/talon-recall ~/.talon/user/recall

# Windows
git clone https://github.com/trillium/talon-recall "%APPDATA%\Talon\user\recall"
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

### Pressing Enter

Recall uses **ender words** — a word you say at the end of a phrase to press Enter. The default ender word is **"bravely"**.

There are three ways to use it:

```
"bravely"                     → just presses Enter (in dictation/mixed mode)
"hello world bravely"         → types "hello world" then presses Enter
"edgar hello world bravely"   → switches to edgar, types, then presses Enter
```

The ender word is configurable — edit `dictation_ender.talon-list` to change it or add alternatives. The `$` end-of-utterance marker ensures the ender word is only recognized at the very end of what you say, so it won't interfere with normal dictation containing the word mid-sentence.

In command mode, you can also say `"slap"` to press Enter.

### Pressing a number key

Say the name followed by a number:

```
"edgar 1"
```

This switches to the window and presses the number key. Useful for selecting numbered options in CLI tools.

## All commands

### Core

| Command | What it does |
|---------|-------------|
| `"recall assign <name>"` | Save the focused window |
| `"<name>"` | Switch to a saved window |
| `"<name> <dictation>"` | Dictate text into a window |
| `"<name> <dictation> bravely"` | Dictate + press Enter |
| `"<name> bravely"` | Switch to window + press Enter |
| `"<name> <number>"` | Press a number key |
| `"bravely"` | Press Enter (dictation/mixed mode) |
| `"<dictation> bravely"` | Type + press Enter (dictation/mixed mode) |

### Aliases and naming

| Command | What it does |
|---------|-------------|
| `"recall alias <name> <alias>"` | Add an alternate name |
| `"recall unalias <name>"` | Remove an alias |
| `"recall rename <name> <new>"` | Change a window's name |
| `"recall promote <alias>"` | Make an alias the primary name |
| `"recall combine <a> <b>"` | Merge b as alias of a |

### Terminal restoration

| Command | What it does |
|---------|-------------|
| `"recall restore <name>"` | Relaunch a terminal at saved path |
| `"recall revive <name>"` | Restore a forgotten/archived terminal |

### Default commands

Recall can run a shell command automatically when restoring a terminal window. Commands are defined in `recall_commands.talon-list`:

```
list: user.recall_commands
-
yolo: yolo
yolo resume: yolo --resume
dev server: npm run dev
build: npm run build
```

The left side is the spoken name, the right side is the shell command. When restoring a window, Recall waits for the terminal to be ready (detects title change) before typing the command.

| Command | What it does |
|---------|-------------|
| `"recall config <name> <command>"` | Set the default command for a window |
| `"recall config <name> clear"` | Remove the default command |
| `"recall edit commands"` | Open the commands list in your editor |

### Window lifecycle

When a saved window closes, Recall preserves the entry (name, path, aliases, command) with a cleared window ID. This means `recall restore` can relaunch it later without losing any configuration.

Forgetting a window moves it to an archive rather than deleting it permanently:

| Command | What it does |
|---------|-------------|
| `"recall forget <name>"` | Archive a saved window |
| `"recall forget all"` | Archive everything |
| `"recall archive"` | Show archived window names |
| `"recall revive <name>"` | Restore an archived terminal |
| `"recall purge <name>"` | Permanently delete from archive |

### Overlays

| Command | What it does |
|---------|-------------|
| `"recall list"` | Flash name labels on all windows (5s) |
| `"recall help"` | Full-screen help panel with all windows, metadata, and commands |
| `"recall close"` | Dismiss any overlay (also Esc key) |

The **help panel** shows each saved window with:
- Status indicator (green = running, red = closed)
- Name and aliases
- App name
- Assigned command (in accent color)
- Terminal path or full execution command (`cd /path && command`)
- Complete command reference

### Focus and window switching

| Command | What it does |
|---------|-------------|
| `"focus <app>"` | Switch to a running application by name |
| `"focus last"` | Switch to the previously focused application |
| `"window next"` | Cycle to the next window of the current app |
| `"window last"` / `"window previous"` | Cycle to the previous window |
| `"running list"` | Show/hide a list of running applications |
| `"running close"` | Hide the running applications list |
| `"launch <app>"` | Launch an application by name |

### Basic keyboard commands

These are included so you can operate without talonhub/community:

| Command | Key |
|---------|-----|
| `"slap"` | Enter |
| `"bravely"` | Enter (dictation/mixed mode — configurable ender word) |
| `"escape"` | Escape |
| `"junk"` | Backspace |
| `"tabby"` | Tab |
| `"go up/down/left/right"` | Arrow keys |
| `"undo"` / `"redo"` | Ctrl+Z / Ctrl+Shift+Z |
| `"copy this"` / `"paste this"` / `"cut this"` | Clipboard |
| `"select all"` | Ctrl+A |

## Terminal path tracking

Recall tracks working directories for terminal windows by parsing the window title (the `user@host: /path` pattern set by most shells). It also listens for title changes in real time, so the path stays current as you `cd` around — even if a program like Claude Code later overwrites the terminal title.

Supported terminals: gnome-terminal, mate-terminal, kitty, Alacritty, foot, xfce4-terminal, Terminator, Tilix.

## Customization

### Ender words

The word "bravely" triggers Enter after dictation. You can change it or add alternatives by editing `dictation_ender.talon-list`:

```
list: user.dictation_ender
-
bravely: bravely
boldly: boldly
```

With multiple enders defined, any of them will work at the end of a phrase. The word was chosen because it almost never appears at the end of naturally dictated text, so it won't trigger accidentally.

### Forbidden names

Some words can't be used as window names because they conflict with commands. Edit `forbidden_recall_names.talon-list` to add or remove reserved words.

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

Recall saves window references (ID, app name, title, terminal path, aliases, default command) to `saved_windows.json` in the package directory. When you say a window's name, it finds the window by ID, focuses it, and updates the terminal path if applicable.

For terminals, Recall detects the working directory by parsing the window title (e.g., `user@host: /path`). A real-time title listener captures path changes as they happen, so the saved path stays accurate even when programs overwrite the terminal title.

When a window can't be found by ID, Recall attempts a re-match by app name and title/path before giving up. Closed windows keep their configuration so they can be restored later.

The `restore` command launches a new terminal at the saved path and optionally runs the configured default command once the shell is ready.

## Using with talonhub/community

If you install [talonhub/community](https://github.com/talonhub/community), recall automatically uses community's richer implementations for:

- Text dictation (with auto-capitalization and spacing)
- Number recognition (full range, not just 0-20)
- Window focusing (with timeout and error handling)
- Spoken form generation (smarter name matching)
- File editing (opens in your configured editor)

The `basic_keys.talon` and `modes.talon` files in this package may conflict with community's versions. If you install community, you can safely delete those two files — community provides its own comprehensive key and mode commands.

## License

MIT
