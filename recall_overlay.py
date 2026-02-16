"""
Recall Overlay - Temporary window name labels + help screen

Shows a name tag on each saved window for 5 seconds,
triggered by "recall list" / "list recalls".
Windows that can't be found are shown in red at the top of the screen.

"recall help" shows a full-screen panel with all saved windows,
their metadata, and a command reference. Auto-hides after 30s.
"""

from talon import cron, registry, skia, ui
from talon.canvas import Canvas
from talon.screen import Screen
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.ui import Rect

canvas: Canvas = None
_hide_job = None

# Padding and styling constants
PAD_X = 20
PAD_Y = 12
FONT_SIZE = 48
SHOW_DURATION = "5s"
MISSING_GAP = 10  # vertical gap between stacked missing-window labels

# Help overlay globals
_help_canvas: Canvas = None
_help_hide_job = None

# Help overlay styling
HELP_BG_COLOR = "000000cc"
HELP_PANEL_COLOR = "1a1a2eee"
HELP_PANEL_BORDER = "4a4a8a"
HELP_HEADER_SIZE = 36
HELP_NAME_SIZE = 24
HELP_DETAIL_SIZE = 16
HELP_CMD_SIZE = 16
HELP_SECTION_SIZE = 20
HELP_TEXT_COLOR = "ffffffff"
HELP_DIM_COLOR = "aaaaaa"
HELP_GREEN = "44cc44"
HELP_RED = "cc4444"
HELP_ACCENT = "6a6aff"
HELP_LINE_COLOR = "4a4a6a"
HELP_PANEL_PAD = 40
HELP_ROW_PAD = 16
HELP_CORNER_RADIUS = 16
PILL_CORNER_RADIUS = 12
COMBINE_CORNER_RADIUS = 16


def _draw_rounded_rect(c: SkiaCanvas, rect: Rect, radius: float):
    """Draw a rounded rectangle using a Skia path."""
    r = min(radius, rect.width / 2, rect.height / 2)
    path = skia.Path()
    path.add_rounded_rect(rect, r, r, skia.Path.Direction.CW)
    c.draw_path(path)


def _get_saved_windows():
    """Import saved_windows lazily to avoid circular imports."""
    from .recall import saved_windows, find_window_by_id
    return saved_windows, find_window_by_id


def _update_overlay_tag():
    """Set or clear the overlay_visible tag based on active canvases."""
    from .recall import overlay_ctx
    if canvas or _help_canvas or _prompt_canvas:
        overlay_ctx.tags = ["user.recall_overlay_visible"]
    else:
        overlay_ctx.tags = []


def on_draw(c: SkiaCanvas):
    saved_windows, find_window_by_id = _get_saved_windows()
    screen = ui.main_screen()

    missing_y_offset = 80  # start below top bar area

    for name, info in saved_windows.items():
        window = find_window_by_id(info["id"])

        c.paint.textsize = FONT_SIZE
        text_rect = c.paint.measure_text(name)[1]
        text_w = text_rect.width
        text_h = text_rect.height

        pill_w = text_w + PAD_X * 2
        pill_h = text_h + PAD_Y * 2

        if window is not None:
            rect = window.rect
            if rect.width <= 0 or rect.height <= 0:
                continue

            # Center label on window
            center_x = rect.x + rect.width / 2
            center_y = rect.y + rect.height / 2
            pill_x = center_x - pill_w / 2
            pill_y = center_y - pill_h / 2
            text_x = center_x - text_w / 2
            text_y = center_y + text_h / 2
            bg_color = "000000bb"
            text_color = "ffffffff"
        else:
            # Show missing windows at top-center of screen in red
            display = f"{name} (not found)"
            c.paint.textsize = FONT_SIZE
            text_rect = c.paint.measure_text(display)[1]
            text_w = text_rect.width
            text_h = text_rect.height
            pill_w = text_w + PAD_X * 2
            pill_h = text_h + PAD_Y * 2

            center_x = screen.rect.x + screen.rect.width / 2
            pill_x = center_x - pill_w / 2
            pill_y = missing_y_offset
            text_x = center_x - text_w / 2
            text_y = missing_y_offset + PAD_Y + text_h
            bg_color = "aa0000cc"
            text_color = "ffffffff"
            name = display
            missing_y_offset += pill_h + MISSING_GAP

        # Draw background
        c.paint.style = c.paint.Style.FILL
        c.paint.color = bg_color
        _draw_rounded_rect(c, Rect(pill_x, pill_y, pill_w, pill_h), PILL_CORNER_RADIUS)

        # Draw text
        c.paint.style = c.paint.Style.FILL
        c.paint.color = text_color
        c.draw_text(name, text_x, text_y)


def show_overlay():
    """Show labels on all saved windows for 5 seconds."""
    global canvas, _hide_job

    # Cancel any pending hide
    if _hide_job:
        cron.cancel(_hide_job)
        _hide_job = None

    # Tear down existing canvas before creating new one
    if canvas:
        canvas.unregister("draw", on_draw)
        canvas.close()
        canvas = None

    saved_windows, _ = _get_saved_windows()
    if not saved_windows:
        return

    screen: Screen = ui.main_screen()
    canvas = Canvas.from_screen(screen)
    canvas.register("draw", on_draw)
    canvas.freeze()

    # Auto-hide after duration
    _hide_job = cron.after(SHOW_DURATION, hide_overlay)
    _update_overlay_tag()


def hide_overlay():
    """Hide and destroy the overlay canvas."""
    global canvas, _hide_job
    if _hide_job:
        cron.cancel(_hide_job)
        _hide_job = None
    if canvas:
        canvas.unregister("draw", on_draw)
        canvas.close()
        canvas = None
    _update_overlay_tag()


# ── Help overlay ──────────────────────────────────────────────────────

HELP_COMMANDS = [
    ('"recall assign <name>"', "save focused window"),
    ('"<name>"', "switch to window"),
    ('"<name> <number>"', "press number key"),
    ('"<name> <dictation>"', "dictate into window"),
    ('"<name> <dictation> <ender>"', "dictate + Enter"),
    ('"recall restore <name>"', "relaunch terminal"),
    ('"recall alias <name> …"', "add alias"),
    ('"recall combine <a> <b>"', "merge b as alias of a"),
    ('"recall rename <name> <new>"', "change canonical name"),
    ('"recall promote <alias>"', "make alias the primary name"),
    ('"recall list"', "show labels on windows"),
    ('"recall help"', "this screen"),
    ('"recall forget <name>"', "remove"),
    ('"recall forget all"', "clear all"),
    ('"recall close"', "dismiss overlay"),
]


def on_draw_help(c: SkiaCanvas):
    saved_windows, find_window_by_id = _get_saved_windows()
    screen = ui.main_screen()
    sr = screen.rect

    # Full-screen dim background
    c.paint.style = c.paint.Style.FILL
    c.paint.color = HELP_BG_COLOR
    c.draw_rect(Rect(sr.x, sr.y, sr.width, sr.height))

    # Calculate panel dimensions
    panel_w = sr.width * 0.55
    panel_x = sr.x + (sr.width - panel_w) / 2

    # Pre-calculate total height needed
    y_cursor = 0  # relative to panel top
    y_cursor += HELP_PANEL_PAD  # top padding
    y_cursor += HELP_HEADER_SIZE + 20  # header + gap

    # Sort: active windows first, then missing
    window_names = sorted(
        saved_windows.keys(),
        key=lambda n: 0 if find_window_by_id(saved_windows[n]["id"]) else 1,
    )
    for name in window_names:
        info = saved_windows[name]
        y_cursor += HELP_NAME_SIZE + 8  # name line (aliases now inline)
        if info.get("path"):
            y_cursor += HELP_DETAIL_SIZE + 4
        y_cursor += HELP_ROW_PAD  # row gap (includes separator)

    if window_names:
        y_cursor += 12  # extra gap before commands section

    # Commands section
    y_cursor += HELP_SECTION_SIZE + 16  # "Commands" header + gap
    y_cursor += len(HELP_COMMANDS) * (HELP_CMD_SIZE + 10)
    y_cursor += HELP_PANEL_PAD  # bottom padding

    panel_h = y_cursor
    panel_y = sr.y + (sr.height - panel_h) / 2

    # Clamp panel to screen if too tall
    if panel_h > sr.height - 40:
        panel_h = sr.height - 40
        panel_y = sr.y + 20

    # Draw panel background
    c.paint.color = HELP_PANEL_COLOR
    panel_rect = Rect(panel_x, panel_y, panel_w, panel_h)
    _draw_rounded_rect(c, panel_rect, HELP_CORNER_RADIUS)

    # Draw panel border
    c.paint.style = c.paint.Style.STROKE
    c.paint.stroke_width = 2
    c.paint.color = HELP_PANEL_BORDER
    _draw_rounded_rect(c, panel_rect, HELP_CORNER_RADIUS)
    c.paint.style = c.paint.Style.FILL

    # Content area
    cx = panel_x + HELP_PANEL_PAD
    cy = panel_y + HELP_PANEL_PAD
    content_w = panel_w - HELP_PANEL_PAD * 2

    # Header
    c.paint.textsize = HELP_HEADER_SIZE
    c.paint.color = HELP_TEXT_COLOR
    c.draw_text("Recall Windows", cx, cy + HELP_HEADER_SIZE)

    # Close hint + X — top-right corner (text then X)
    close_text = '"recall close" or Esc to close'
    c.paint.textsize = HELP_DETAIL_SIZE
    c.paint.color = HELP_DIM_COLOR
    close_w = c.paint.measure_text(close_text)[1].width
    x_size = 14
    gap = 10
    total_w = close_w + gap + x_size
    close_x = panel_x + panel_w - HELP_PANEL_PAD - total_w
    c.draw_text(close_text, close_x, panel_y + HELP_PANEL_PAD + HELP_DETAIL_SIZE)

    # X button (right of text)
    x_x = close_x + close_w + gap
    x_cy = panel_y + HELP_PANEL_PAD + HELP_DETAIL_SIZE / 2
    c.paint.style = c.paint.Style.STROKE
    c.paint.stroke_width = 2
    c.paint.color = HELP_DIM_COLOR
    c.draw_line(x_x, x_cy - x_size / 2, x_x + x_size, x_cy + x_size / 2)
    c.draw_line(x_x, x_cy + x_size / 2, x_x + x_size, x_cy - x_size / 2)
    c.paint.style = c.paint.Style.FILL

    cy += HELP_HEADER_SIZE + 20

    # Window rows
    for name in window_names:
        info = saved_windows[name]
        window = find_window_by_id(info["id"])

        # Status dot
        dot_radius = 5
        dot_x = cx + dot_radius
        dot_y = cy + HELP_NAME_SIZE / 2 + 2
        c.paint.color = HELP_GREEN if window else HELP_RED
        c.draw_circle(dot_x, dot_y, dot_radius)

        # Name + aliases as one string: name / alias1 / alias2    AppName
        name_x = cx + dot_radius * 2 + 12
        aliases = info.get("aliases", [])
        all_names = " / ".join([name] + aliases)
        app_name = info.get("app", "")
        if app_name:
            display = f"{all_names}    {app_name}"
        else:
            display = all_names

        c.paint.textsize = HELP_NAME_SIZE
        c.paint.color = HELP_TEXT_COLOR
        c.draw_text(display, name_x, cy + HELP_NAME_SIZE)

        cy += HELP_NAME_SIZE + 8

        # Path
        path = info.get("path")
        if path:
            c.paint.textsize = HELP_DETAIL_SIZE
            c.paint.color = HELP_DIM_COLOR
            c.draw_text(path, name_x, cy + HELP_DETAIL_SIZE)
            cy += HELP_DETAIL_SIZE + 4

        cy += HELP_ROW_PAD

        # Separator line
        c.paint.style = c.paint.Style.STROKE
        c.paint.stroke_width = 1
        c.paint.color = HELP_LINE_COLOR
        c.draw_line(cx, cy - HELP_ROW_PAD / 2, cx + content_w, cy - HELP_ROW_PAD / 2)
        c.paint.style = c.paint.Style.FILL

    if window_names:
        cy += 12

    # Commands section header
    c.paint.textsize = HELP_SECTION_SIZE
    c.paint.color = HELP_ACCENT
    c.draw_text("Commands", cx, cy + HELP_SECTION_SIZE)
    cy += HELP_SECTION_SIZE + 16

    # Build command list, replacing <ender> with actual ender words
    ender_words = sorted(registry.lists.get("user.dictation_ender", [{}])[-1].keys())
    if len(ender_words) > 1:
        ender_label = "(" + " | ".join(ender_words) + ")"
    elif ender_words:
        ender_label = ender_words[0]
    else:
        ender_label = "bravely"
    commands = [
        (cmd.replace("<ender>", ender_label), desc)
        for cmd, desc in HELP_COMMANDS
    ]

    # Command rows
    cmd_col_w = content_w * 0.5
    for cmd, desc in commands:
        c.paint.textsize = HELP_CMD_SIZE
        c.paint.color = HELP_TEXT_COLOR
        c.draw_text(cmd, cx, cy + HELP_CMD_SIZE)
        c.paint.color = HELP_DIM_COLOR
        c.draw_text(desc, cx + cmd_col_w, cy + HELP_CMD_SIZE)
        cy += HELP_CMD_SIZE + 10


def show_help():
    """Show the full help overlay with all saved windows and commands."""
    global _help_canvas, _help_hide_job

    if _help_hide_job:
        cron.cancel(_help_hide_job)
        _help_hide_job = None

    if _help_canvas:
        _help_canvas.unregister("draw", on_draw_help)
        _help_canvas.close()
        _help_canvas = None

    screen: Screen = ui.main_screen()
    _help_canvas = Canvas.from_screen(screen)
    _help_canvas.register("draw", on_draw_help)
    _update_overlay_tag()


def hide_help():
    """Hide and destroy the help overlay canvas."""
    global _help_canvas, _help_hide_job
    if _help_hide_job:
        cron.cancel(_help_hide_job)
        _help_hide_job = None
    if _help_canvas:
        _help_canvas.unregister("draw", on_draw_help)
        _help_canvas.close()
        _help_canvas = None
    _update_overlay_tag()


def hide_any():
    """Hide whichever overlay is currently active."""
    hide_overlay()
    hide_help()
    hide_prompt()


# ── Prompt overlay (used by combine, rename, alias) ──────────────────

_prompt_canvas: Canvas = None
_prompt_hide_job = None
_prompt_title: str = ""
_prompt_subtitle: str = ""
PROMPT_DURATION = "15s"
PROMPT_CORNER_RADIUS = 16


def on_draw_prompt(c: SkiaCanvas):
    screen = ui.main_screen()
    sr = screen.rect

    # Dim background
    c.paint.style = c.paint.Style.FILL
    c.paint.color = HELP_BG_COLOR
    c.draw_rect(Rect(sr.x, sr.y, sr.width, sr.height))

    # Centered prompt panel
    panel_w = sr.width * 0.4
    panel_h = 180
    panel_x = sr.x + (sr.width - panel_w) / 2
    panel_y = sr.y + (sr.height - panel_h) / 2

    c.paint.color = HELP_PANEL_COLOR
    prompt_rect = Rect(panel_x, panel_y, panel_w, panel_h)
    _draw_rounded_rect(c, prompt_rect, PROMPT_CORNER_RADIUS)

    c.paint.style = c.paint.Style.STROKE
    c.paint.stroke_width = 2
    c.paint.color = HELP_ACCENT
    _draw_rounded_rect(c, prompt_rect, PROMPT_CORNER_RADIUS)
    c.paint.style = c.paint.Style.FILL

    cx = panel_x + HELP_PANEL_PAD
    cy = panel_y + HELP_PANEL_PAD

    # Title
    c.paint.textsize = HELP_NAME_SIZE
    c.paint.color = HELP_TEXT_COLOR
    c.draw_text(_prompt_title, cx, cy + HELP_NAME_SIZE)
    cy += HELP_NAME_SIZE + 20

    # Subtitle
    c.paint.textsize = HELP_DETAIL_SIZE
    c.paint.color = HELP_DIM_COLOR
    c.draw_text(_prompt_subtitle, cx, cy + HELP_DETAIL_SIZE)
    cy += HELP_DETAIL_SIZE + 16

    c.paint.textsize = HELP_DETAIL_SIZE
    c.paint.color = HELP_DIM_COLOR
    c.draw_text('"recall close" to cancel', cx, cy + HELP_DETAIL_SIZE)


def show_prompt(title: str, subtitle: str):
    """Show a prompt overlay with custom title and subtitle."""
    global _prompt_canvas, _prompt_hide_job, _prompt_title, _prompt_subtitle
    _prompt_title = title
    _prompt_subtitle = subtitle

    if _prompt_hide_job:
        cron.cancel(_prompt_hide_job)
        _prompt_hide_job = None

    if _prompt_canvas:
        _prompt_canvas.unregister("draw", on_draw_prompt)
        _prompt_canvas.close()
        _prompt_canvas = None

    screen: Screen = ui.main_screen()
    _prompt_canvas = Canvas.from_screen(screen)
    _prompt_canvas.register("draw", on_draw_prompt)
    _prompt_canvas.freeze()

    _prompt_hide_job = cron.after(PROMPT_DURATION, hide_prompt)
    _update_overlay_tag()


def hide_prompt():
    """Hide the prompt overlay and cancel pending state."""
    global _prompt_canvas, _prompt_hide_job
    if _prompt_hide_job:
        cron.cancel(_prompt_hide_job)
        _prompt_hide_job = None
    if _prompt_canvas:
        _prompt_canvas.unregister("draw", on_draw_prompt)
        _prompt_canvas.close()
        _prompt_canvas = None
    from .recall import _cancel_pending
    _cancel_pending()
    _update_overlay_tag()


# ── Flash notification ────────────────────────────────────────────────

_flash_canvas: Canvas = None
_flash_hide_job = None
_flash_message: str = ""
FLASH_DURATION = "2500ms"
FLASH_FONT_SIZE = 20
FLASH_PAD_X = 28
FLASH_PAD_Y = 16
FLASH_BG = "1a1a2eee"
FLASH_BORDER = "6a6aff"
FLASH_TEXT = "ffffffff"
FLASH_CORNER = 12


def on_draw_flash(c: SkiaCanvas):
    screen = ui.main_screen()
    sr = screen.rect

    c.paint.textsize = FLASH_FONT_SIZE
    text_rect = c.paint.measure_text(_flash_message)[1]
    text_w = text_rect.width
    text_h = text_rect.height

    pill_w = text_w + FLASH_PAD_X * 2
    pill_h = text_h + FLASH_PAD_Y * 2
    pill_x = sr.x + (sr.width - pill_w) / 2
    pill_y = sr.y + sr.height * 0.35 - pill_h / 2

    # Background
    c.paint.style = c.paint.Style.FILL
    c.paint.color = FLASH_BG
    pill_rect = Rect(pill_x, pill_y, pill_w, pill_h)
    _draw_rounded_rect(c, pill_rect, FLASH_CORNER)

    # Border
    c.paint.style = c.paint.Style.STROKE
    c.paint.stroke_width = 2
    c.paint.color = FLASH_BORDER
    _draw_rounded_rect(c, pill_rect, FLASH_CORNER)
    c.paint.style = c.paint.Style.FILL

    # Text
    c.paint.color = FLASH_TEXT
    c.paint.textsize = FLASH_FONT_SIZE
    text_x = pill_x + FLASH_PAD_X
    text_y = pill_y + FLASH_PAD_Y + text_h
    c.draw_text(_flash_message, text_x, text_y)


def flash(message: str):
    """Show a brief centered notification pill."""
    global _flash_canvas, _flash_hide_job, _flash_message
    _flash_message = message

    if _flash_hide_job:
        cron.cancel(_flash_hide_job)
        _flash_hide_job = None

    if _flash_canvas:
        _flash_canvas.unregister("draw", on_draw_flash)
        _flash_canvas.close()
        _flash_canvas = None

    screen: Screen = ui.main_screen()
    _flash_canvas = Canvas.from_screen(screen)
    _flash_canvas.register("draw", on_draw_flash)
    _flash_canvas.freeze()

    _flash_hide_job = cron.after(FLASH_DURATION, hide_flash)


def hide_flash():
    """Hide the flash notification."""
    global _flash_canvas, _flash_hide_job
    if _flash_hide_job:
        cron.cancel(_flash_hide_job)
        _flash_hide_job = None
    if _flash_canvas:
        _flash_canvas.unregister("draw", on_draw_flash)
        _flash_canvas.close()
        _flash_canvas = None
