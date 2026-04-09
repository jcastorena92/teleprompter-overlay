"""
Teleprompter OBS

Custom Python teleprompter designed for:
- OBS recording
- Minimal eye movement
- Ghost mode (transparent overlay)

Author: Juan Carlos Castorena
"""

import json
import argparse
import tkinter as tk
from pathlib import Path
import textwrap

# Get the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent
# Default configuration file path
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"

# Default configuration settings for the teleprompter application
DEFAULT_CONFIG = {
    "window_title": "Teleprompter OBS",
    "width": 1000,
    "height": 600,
    "bg_color": "black",
    "fg_color": "white",
    "font_family": "Arial",
    "font_size": 28,
    "min_font_size": 20,
    "text_width": 380,
    "always_on_top": True,
    "transparency": 1.0,
    "scroll_interval_ms": 30,
    "scroll_step": 1.2,
    "initial_speed": 0.7,
    "start_running": False,
    "show_status_bar": True,
    "status_bar_position": "bottom",
    "auto_hide_status_bar": True,
    "status_bar_hide_ms": 1800,
    "top_spacer": 120,
    "reading_window_lines": 4,
    "line_height_factor": 1.35,
    "reading_window_offset_y": -90,
    "ghost_mode": True,
    "ghost_window_width": 420,
    "dim_color": "black",
    "show_guide_line": True,
    "guide_line_color": "#505050",
    "guide_line_width": 1,
    "guide_line_offset_y": 0,
}


def load_config(config_path: Path) -> dict:
    """
    Load configuration from JSON file, merging with defaults.

    Args:
        config_path: Path to the JSON configuration file.

    Returns:
        Dictionary with merged configuration (defaults + user config).
    """
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as file:
                user_config = json.load(file)
            merged = DEFAULT_CONFIG.copy()
            merged.update(user_config)
            return merged
        except (json.JSONDecodeError, OSError):
            print("Aviso: no se pudo leer el archivo de configuración.")
    return DEFAULT_CONFIG.copy()


def load_text(file_path: Path) -> str:
    """
    Load text content from file.

    Args:
        file_path: Path to the text file to load.

    Returns:
        String containing the file content or an error message.
    """
    if not file_path.exists():
        return "ERROR: No se encontró el archivo de guion."

    text = file_path.read_text(encoding="utf-8").strip()

    if not text:
        return "ERROR: El archivo existe pero está vacío."

    return text


def wrap_text_smart(text: str, max_chars: int) -> str:
    """
    Wrap text intelligently preserving paragraph structure.

    Args:
        text: The text to wrap.
        max_chars: Maximum characters per line.

    Returns:
        Wrapped text with preserved paragraphs.
    """
    wrapped_paragraphs = []

    for paragraph in text.splitlines():
        if not paragraph.strip():
            wrapped_paragraphs.append("")
            continue

        # Wrap without breaking words or hyphens
        wrapped = textwrap.fill(
            paragraph,
            width=max_chars,
            break_long_words=False,
            break_on_hyphens=False,
        )
        wrapped_paragraphs.append(wrapped)

    return "\n".join(wrapped_paragraphs)


class Teleprompter:
    """
    Main teleprompter application.

    Handles:
    - UI rendering (Tkinter canvas)
    - Text scrolling logic
    - Ghost mode overlay
    - Keyboard interaction
    """

    def __init__(self, root: tk.Tk, text_content: str, config: dict):
        """
        Initialize the teleprompter UI and state.

        Args:
            root: The Tkinter root window.
            text_content: The script text to display.
            config: Configuration dictionary.
        """
        self.root = root
        self.config = config
        self.raw_text_content = text_content

        # Initialize playback state
        self.running = bool(config["start_running"])
        self.speed = float(config["initial_speed"])
        self.scroll_position = 0.0

        # Configure main window
        self.root.title(config["window_title"])
        self.root.geometry(f"{config['width']}x{config['height']}")
        self.root.configure(bg=config["bg_color"])
        self.root.attributes("-topmost", config["always_on_top"])

        # Ghost mode:
        # Uses transparency and overlay positioning to make the teleprompter
        # less visually intrusive for the user while recording.
        # Note: this does not guarantee invisibility in OBS Display Capture.
        # To keep it out of the recording, use Window Capture, another monitor,
        # or keep the teleprompter outside the captured region.
        self.root.attributes("-alpha", config["transparency"])

        # Create main frame
        self.main_frame = tk.Frame(self.root, bg=config["bg_color"])
        self.main_frame.pack(fill="both", expand=True)

        # Initialize status bar
        self.status_var = tk.StringVar()
        self.status_var.set(self._build_status_text())

        self.status_label = None
        self.status_hide_job = None

        if config.get("show_status_bar", True):
            self.status_label = tk.Label(
                self.main_frame,
                textvariable=self.status_var,
                bg=config["bg_color"],
                fg=config["fg_color"],
                font=(config["font_family"], 11),
                anchor="w",
                padx=10,
                pady=8,
            )

            # Place status bar at top or bottom
            if config.get("status_bar_position", "bottom") == "top":
                self.status_label.pack(side="top", fill="x")
            else:
                self.status_label.pack(side="bottom", fill="x")

        # Create canvas for text rendering
        self.canvas = tk.Canvas(
            self.main_frame,
            bg=config["bg_color"],
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.text_id = None

        self._bind_keys()

        # Initialize UI after window is drawn
        self.root.after(100, self._initialize_ui)
        # Start scroll loop
        self.root.after(config["scroll_interval_ms"], self.scroll_loop)

    def _initialize_ui(self):
        """Initialize UI after window is created."""
        self.root.focus_force()
        self.canvas.focus_force()
        self._draw_text()
        self._show_status_temporarily()

    def _bind_keys(self):
        """Bind keyboard shortcuts to their respective handler functions."""
        self.root.bind_all("<space>", self.toggle)
        self.root.bind_all("<Up>", self.speed_up)
        self.root.bind_all("<Down>", self.speed_down)
        self.root.bind_all("r", self.reset_position)
        self.root.bind_all("<Escape>", self.close)
        self.root.bind_all("<plus>", self.font_up)
        self.root.bind_all("<KP_Add>", self.font_up)
        self.root.bind_all("<minus>", self.font_down)
        self.root.bind_all("<KP_Subtract>", self.font_down)
        self.root.bind_all("<Next>", self.manual_down)  # PageDown
        self.root.bind_all("<Prior>", self.manual_up)  # PageUp
        self.root.bind_all("<MouseWheel>", self.on_mousewheel)
        self.root.bind("<Configure>", self._on_resize)

    def _build_status_text(self) -> str:
        """
        Build status bar text with current state and controls.

        Returns:
            Formatted string with status information and key bindings.
        """
        state = "REPRODUCIENDO" if self.running else "PAUSADO"
        return (
            f"{state} | Velocidad: {self.speed:.1f} | "
            "Espacio iniciar/pausar | ↑/↓ velocidad | "
            "PageUp/PageDown mover | +/- fuente | r reiniciar | Esc salir"
        )

    def update_status(self):
        """Update status bar display and show it temporarily."""
        self.status_var.set(self._build_status_text())
        self._show_status_temporarily()

    def _show_status_temporarily(self):
        """Show status bar temporarily if auto-hide is enabled."""
        if not self.status_label or not self.config.get("auto_hide_status_bar", False):
            return

        # Repack status bar
        self.status_label.pack_forget()

        if self.config.get("status_bar_position", "bottom") == "top":
            self.status_label.pack(side="top", fill="x")
        else:
            self.status_label.pack(side="bottom", fill="x")

        # Cancel previous hide job
        if self.status_hide_job:
            self.root.after_cancel(self.status_hide_job)

        # Schedule auto-hide
        hide_ms = int(self.config.get("status_bar_hide_ms", 1800))
        self.status_hide_job = self.root.after(
            hide_ms, self._hide_status_bar_if_running
        )

    def _hide_status_bar_if_running(self):
        """Hide status bar if playback is running."""
        if self.status_label and self.running:
            self.status_label.pack_forget()

    def _estimate_max_chars(self) -> int:
        """
        Estimate maximum characters per line based on canvas width.

        Returns:
            Maximum number of characters that fit on one line.
        """
        text_width = int(self.config["text_width"])
        font_size = int(self.config["font_size"])

        estimated = max(10, int(text_width / max(font_size * 0.55, 1)))
        return estimated

    def _get_dynamic_font_size(self):
        """
        Adjust font size based on longest word length.

        Returns:
            Integer font size adjusted for content.
        """
        words = self.raw_text_content.split()
        if not words:
            return self.config["font_size"]

        longest = max(words, key=len)
        length = len(longest)

        base = self.config["font_size"]
        min_size = self.config.get("min_font_size", 16)

        # Reduce font size for long words
        if length > 14:
            return max(base - 6, min_size)
        elif length > 12:
            return max(base - 4, min_size)
        elif length > 10:
            return max(base - 2, min_size)
        else:
            return base

    def _get_wrapped_text(self):
        """
        Get text wrapped to appropriate line width.

        Returns:
            Wrapped text string.
        """
        max_chars = self._estimate_max_chars()
        return wrap_text_smart(self.raw_text_content, max_chars=max_chars)

    def _reading_window_geometry(self):
        """
        Calculate the reading window rectangle coordinates.

        Returns:
            Tuple of (left, top, right, bottom) coordinates in pixels.
        """
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        font_size = self._get_dynamic_font_size()
        lines = self.config.get("reading_window_lines", 4)
        line_factor = self.config.get("line_height_factor", 1.35)

        # Calculate reading window height
        line_px = font_size * line_factor
        window_h = int(lines * line_px)

        # Calculate vertical position
        center_y = canvas_h // 2 + int(self.config.get("reading_window_offset_y", 0))
        top = max(0, center_y - window_h // 2)
        bottom = min(canvas_h, center_y + window_h // 2)

        # Calculate horizontal position
        ghost_window_width = int(
            self.config.get("ghost_window_width", self.config["text_width"] + 60)
        )
        center_x = canvas_w // 2
        left = max(0, center_x - ghost_window_width // 2)
        right = min(canvas_w, center_x + ghost_window_width // 2)

        return left, top, right, bottom

    def _draw_ghost_masks(self):
        """Draw dimmed areas outside the reading window (ghost mode)."""
        if not self.config.get("ghost_mode", True):
            return

        left, top, right, bottom = self._reading_window_geometry()
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        stipple_style = "gray50"
        dim_color = self.config.get("dim_color", "black")

        # Top mask
        self.canvas.create_rectangle(
            0,
            0,
            canvas_w,
            top,
            fill=dim_color,
            outline="",
            stipple=stipple_style,
        )

        # Bottom mask
        self.canvas.create_rectangle(
            0,
            bottom,
            canvas_w,
            canvas_h,
            fill=dim_color,
            outline="",
            stipple=stipple_style,
        )

        # Left mask
        self.canvas.create_rectangle(
            0,
            top,
            left,
            bottom,
            fill=dim_color,
            outline="",
            stipple=stipple_style,
        )

        # Right mask
        self.canvas.create_rectangle(
            right,
            top,
            canvas_w,
            bottom,
            fill=dim_color,
            outline="",
            stipple=stipple_style,
        )

    def _draw_guide_line(self):
        """Draw a guide line in the center of the reading window."""
        if not self.config.get("show_guide_line", False):
            return

        left, top, right, bottom = self._reading_window_geometry()

        # Calculate guide line vertical position
        guide_y = (
            top + ((bottom - top) // 2) + int(self.config.get("guide_line_offset_y", 0))
        )

        self.canvas.create_line(
            left,
            guide_y,
            right,
            guide_y,
            fill=self.config.get("guide_line_color", "#505050"),
            width=int(self.config.get("guide_line_width", 1)),
        )

    def _draw_text(self):
        """Render text on canvas with all visual effects (ghost mode, guide line)."""
        self.canvas.delete("all")

        canvas_width = self.canvas.winfo_width()
        if canvas_width < 10:
            return

        # Calculate text position
        text_x = canvas_width // 2
        text_y = self.config.get("top_spacer", 120) - self.scroll_position
        dynamic_size = self._get_dynamic_font_size()
        wrapped_text = self._get_wrapped_text()

        # Draw main text
        self.text_id = self.canvas.create_text(
            text_x,
            text_y,
            text=wrapped_text,
            fill=self.config["fg_color"],
            font=(self.config["font_family"], dynamic_size),
            width=self.config["text_width"],
            justify="center",
            anchor="n",
        )

        # Draw visual elements
        self._draw_ghost_masks()
        self._draw_guide_line()

    def _on_resize(self, event=None):
        """Redraw text when window is resized."""
        self._draw_text()

    def toggle(self, event=None):
        """Toggle playback on/off (spacebar)."""
        self.running = not self.running
        self.update_status()

        if not self.running and self.status_label:
            self._show_status_temporarily()

    def speed_up(self, event=None):
        """Increase scroll speed (up arrow)."""
        if self.speed < 5.0:
            self.speed += 0.2
        self.update_status()

    def speed_down(self, event=None):
        """Decrease scroll speed (down arrow)."""
        if self.speed > 0.2:
            self.speed -= 0.2
        self.update_status()

    def manual_down(self, event=None):
        """Scroll down manually (PageDown)."""
        self.scroll_position += 40
        self._draw_text()
        self._show_status_temporarily()

    def manual_up(self, event=None):
        """Scroll up manually (PageUp)."""
        self.scroll_position = max(0, self.scroll_position - 40)
        self._draw_text()
        self._show_status_temporarily()

    def on_mousewheel(self, event):
        """
        Handle mouse wheel scrolling.

        Args:
            event: Mouse wheel event object.
        """
        if event.delta < 0:
            self.scroll_position += 40
        else:
            self.scroll_position = max(0, self.scroll_position - 40)
        self._draw_text()
        self._show_status_temporarily()

    def reset_position(self, event=None):
        """Reset scroll position to top (r key)."""
        self.scroll_position = 0.0
        self._draw_text()
        self.update_status()

    def close(self, event=None):
        """Close application (Escape key)."""
        self.root.destroy()

    def font_up(self, event=None):
        """Increase font size (+ key)."""
        self.config["font_size"] = min(self.config["font_size"] + 2, 72)
        self._draw_text()
        self._show_status_temporarily()

    def font_down(self, event=None):
        """Decrease font size (- key)."""
        min_size = self.config.get("min_font_size", 16)
        self.config["font_size"] = max(self.config["font_size"] - 2, min_size)
        self._draw_text()
        self._show_status_temporarily()

    def scroll_loop(self):
        # Main animation loop (runs continuously using Tkinter's after scheduler)
        if self.running:
            # Update scroll position based on speed
            self.scroll_position += self.config["scroll_step"] * self.speed
            self._draw_text()

        # Schedule next frame
        self.root.after(self.config["scroll_interval_ms"], self.scroll_loop)


def parse_args():
    """
    CLI interface to allow flexible usage from terminal

    Parse command line arguments.

    Returns:
        Parsed arguments object with 'file' and 'config' attributes.

    """

    parser = argparse.ArgumentParser(description="Teleprompter para OBS")
    parser.add_argument("--file", type=str, help="Ruta del archivo de guion")
    parser.add_argument(
        "--config", type=str, help="Ruta del archivo JSON de configuración"
    )
    return parser.parse_args()


def main():
    # Entry point: loads config, reads script, and launches UI
    args = parse_args()

    # Load configuration
    config_path = Path(args.config) if args.config else DEFAULT_CONFIG_PATH
    config = load_config(config_path)

    # Load script text
    if args.file:
        script_path = Path(args.file)
        text_content = load_text(script_path)
        print(f"Guion cargado desde: {script_path}")
        print(f"Primeros 120 caracteres: {text_content[:120]!r}")
    else:
        text_content = (
            "NO SE PROPORCIONÓ NINGÚN ARCHIVO.\n\n"
            "Ejemplo:\n"
            'python teleprompter.py --file "guion.txt" --config "config_obs.json"'
        )
        print("Aviso: no se proporcionó archivo de guion.")

    print("Longitud del texto cargado:", len(text_content))

    # Create and run application
    root = tk.Tk()
    Teleprompter(root, text_content, config)
    root.mainloop()


if __name__ == "__main__":
    main()
