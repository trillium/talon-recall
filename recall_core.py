"""
Recall Core — self-contained shims for Talon community actions and captures.

Provides the minimum actions and captures needed by the recall system
so it works without installing the full Talon community package.

If talonhub/community IS installed, community's richer implementations
are already registered and these shims gracefully skip registration.
The recall system will use whichever version is available.
"""

import re
import time
from talon import Module, Context, actions, ui

mod = Module()
ctx = Context()

# ── Captures ──────────────────────────────────────────────────────────
# Each capture is wrapped in try/except so it silently skips if
# community (or another package) already registered it.

try:
    @mod.capture(rule="<phrase>")
    def text(m) -> str:
        """Free-form dictation text"""
        return str(m)
except Exception:
    pass

try:
    @mod.capture(rule="<phrase>")
    def raw_prose(m) -> str:
        """Raw dictation without formatting"""
        return str(m)
except Exception:
    pass

try:
    mod.list("number_small", desc="Small numbers for voice input")
    ctx.lists["user.number_small"] = {
        "zero": "0", "oh": "0",
        "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
        "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
        "eighteen": "18", "nineteen": "19", "twenty": "20",
    }

    @ctx.capture("number_small", rule="{user.number_small}")
    def number_small(m) -> int:
        return int(m.number_small)
except Exception:
    pass


# ── Actions ───────────────────────────────────────────────────────────
# Actions defined with mod.action_class serve as defaults.
# If community defines the same actions, both coexist and Talon
# uses whichever is most specific to the active context.

@mod.action_class
class Actions:
    def dictation_insert(text: str):
        """Insert dictated text (simple version — just inserts as-is)"""
        actions.insert(text)

    def switcher_focus_window(window: ui.Window):
        """Focus a window and wait for the switch"""
        window.focus()
        t1 = time.perf_counter()
        while ui.active_window() != window:
            if time.perf_counter() - t1 > 1:
                break
            actions.sleep(0.1)

    def create_spoken_forms_from_map(
        sources: dict,
        words_to_exclude: list = None,
        minimum_term_length: int = 1,
        generate_subsequences: bool = True,
    ) -> dict:
        """Create spoken forms from a name map.

        Simple version: lowercases keys and splits underscores/hyphens.
        For each key, generates the full spoken form and (if enabled)
        each individual word as a subsequence.
        """
        result = {}
        for name, value in sources.items():
            spoken = re.sub(r"[-_]+", " ", name.lower()).strip()
            result[spoken] = value
            if generate_subsequences:
                words = spoken.split()
                for word in words:
                    if len(word) >= minimum_term_length:
                        if word not in result:
                            result[word] = value
        return result
