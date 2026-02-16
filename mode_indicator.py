"""
Mode Indicator — a small colored circle showing the current Talon mode.

Colors:
- Grey:   sleep mode (mic on, not listening for commands)
- Blue:   command mode (voice commands only)
- Gold:   dictation mode (typing only)
- Green:  mixed mode (commands + dictation together) ← recommended for recall
- Black:  microphone is off
"""

from talon import Module, actions, app, cron, registry, scope, settings, skia, ui
from talon.canvas import Canvas
from talon.screen import Screen
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia.imagefilter import ImageFilter
from talon.types.point import Point2d
from talon.ui import Rect

canvas: Canvas = None
mod = Module()

_mode = ""
_microphone = ""

mod.setting("mode_indicator_show", type=bool, default=True, desc="Show the mode indicator")
mod.setting("mode_indicator_size", type=float, default=30, desc="Diameter in pixels")
mod.setting("mode_indicator_x", type=float, default=0.5, desc="X position (0=left, 1=right)")
mod.setting("mode_indicator_y", type=float, default=0, desc="Y position (0=top, 1=bottom)")
mod.setting("mode_indicator_color_alpha", type=float, default=0.75, desc="Opacity (0-1)")

# Mode colors
COLORS = {
    "mute": "000000",
    "sleep": "808080",
    "dictation": "ffd700",
    "mixed": "3cb371",
    "command": "6495ed",
    "other": "f8f8ff",
}

setting_paths = {
    "user.mode_indicator_show",
    "user.mode_indicator_size",
    "user.mode_indicator_x",
    "user.mode_indicator_y",
    "user.mode_indicator_color_alpha",
}


def get_mode_color() -> str:
    if _microphone == "None":
        return COLORS["mute"]
    return COLORS.get(_mode, COLORS["other"])


def on_draw(c: SkiaCanvas):
    screen: Screen = ui.main_screen()
    rect = screen.rect
    scale = screen.scale if app.platform != "mac" else 1

    color = get_mode_color()
    alpha_hex = f"{int(settings.get('user.mode_indicator_color_alpha') * 255):02x}"

    radius = settings.get("user.mode_indicator_size") * scale / 2
    cx = rect.left + min(
        max(settings.get("user.mode_indicator_x") * rect.width, radius),
        rect.width - radius,
    )
    cy = rect.top + min(
        max(settings.get("user.mode_indicator_y") * rect.height, radius),
        rect.height - radius,
    )

    c.paint.style = c.paint.Style.FILL
    c.paint.color = f"{color}{alpha_hex}"
    c.paint.imagefilter = ImageFilter.drop_shadow(1, 1, 1, 1, "333333")
    c.draw_circle(cx, cy, radius)
    c.paint.imagefilter = None


def show_indicator():
    global canvas
    screen: Screen = ui.main_screen()
    canvas = Canvas.from_screen(screen)
    canvas.register("draw", on_draw)


def hide_indicator():
    global canvas
    if canvas:
        canvas.unregister("draw", on_draw)
        canvas.close()
        canvas = None


def update_indicator():
    if settings.get("user.mode_indicator_show"):
        if not canvas:
            show_indicator()
        canvas.freeze()
    elif canvas:
        hide_indicator()


def rebuild_indicator():
    if canvas:
        hide_indicator()
    update_indicator()


def _on_update_contexts():
    global _mode
    modes = scope.get("mode")
    if "sleep" in modes:
        _mode = "sleep"
    elif "dictation" in modes:
        _mode = "mixed" if "command" in modes else "dictation"
    elif "command" in modes:
        _mode = "command"
    else:
        _mode = "other"
    update_indicator()


def _poll_microphone():
    global _microphone
    try:
        mic = actions.sound.active_microphone()
    except Exception:
        mic = "unknown"
    if mic != _microphone:
        _microphone = mic
        update_indicator()


def on_update_settings(updated: set[str]):
    if setting_paths & updated:
        rebuild_indicator()


def on_ready():
    registry.register("update_contexts", _on_update_contexts)
    registry.register("update_settings", on_update_settings)
    ui.register("screen_change", lambda _: rebuild_indicator())
    cron.interval("500ms", _poll_microphone)


app.register("ready", on_ready)
