# Teleprompter Overlay for OBS

![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/status-stable-success)
![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen)

> Lightweight, customizable teleprompter with "ghost mode" for OBS-based recording.

A Python-based teleprompter designed for real-world content creation, including video recording, academic presentations, and voice-over work.

---

## Key Features at a Glance

- Centered text optimized for eye movement  
- Smooth auto-scroll  
- Narrow reading column  
- Ghost mode (invisible in OBS recordings)

---

## Demo

![demo](docs/demo.gif)

> Demo preview (see docs/demo.gif)

---

## Quick Start

```bash
git clone https://github.com/jcastorena92/teleprompter-obs-clean.git
cd teleprompter-obs-clean

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

python teleprompter.py
```

> This project runs using only Python’s built-in libraries. The `requirements.txt` file is included for convenience, even though no extra installation is needed — you can safely skip this step.

## Usage

```bash
python teleprompter.py --file path/to/script.txt --config config_obs.json
```

Example:

```bash
python teleprompter.py --file guion.txt --config config_obs.json
```

---

## Problem

When recording videos or presentations, reading from a script often leads to:

- unnatural eye movement
- loss of flow while speaking
- constant switching between windows

Most available solutions are either hardware-based, expensive, or not well adapted to OBS use cases.

---

## Solution

This project provides a lightweight teleprompter implemented in Python with:

- a centered reading window
- smooth automatic scrolling
- keyboard-based control
- a configurable interface via JSON

It is designed to work alongside OBS without disrupting the recording workflow.

---

## Features

- Adjustable reading window
- Narrow text layout for better focus
- Optional ghost mode (dimmed surrounding area)
- Guide line for consistent pacing
- Scroll speed control
- Dynamic font size adjustment
- Optional status bar with auto-hide

---

## How it works

The application is built using:

- `tkinter` for the interface
- a canvas-based rendering system for text
- an event loop (`after`) for smooth scrolling

The “ghost mode” uses layered drawing and dimmed regions to guide focus toward a central reading area.

---

## Controls

- Space: start / pause
- Up / Down: adjust speed
- PageUp / PageDown: manual scroll
- Use + / - to adjust font size
- r: reset position
- Esc: exit

---

## Configuration

Behavior can be customized via a JSON file:

```json
{
  "width": 1000,
  "height": 600,
  "font_size": 28,
  "text_width": 380,
  "ghost_mode": true,
  "scroll_step": 1.2
}
```

---

## Use cases

- video recording
- academic presentations
- voice-over work
- script-based delivery

---

## Notes

This project was built to solve a practical workflow problem: recording structured content while maintaining a natural delivery.

The current implementation includes some console/status messages in Spanish. These user-facing strings are easy to customize and can be translated to any preferred language.

---

## Development history

This public repository preserves the original development history of the project. The commit chain was rewritten only to remove non-public course-specific script files from the initial version before publication.

## Possible Future Improvements

- GUI controls (pause, speed, positioning)
- Voice control integration
- Dynamic script loading
- Multi-language UI support
- OBS plugin integration

---

## License

MIT License © 2026 Juan Carlos Castorena Avalos

---

## Author

Juan Carlos Castorena Avalos

- Aerospace Engineer with specialization in CFD
- Background in languages and translation technologies
- Focused on text processing, OCR, and automation tools

GitHub: [github.com/jcastorena92](https://github.com/jcastorena92)  
LinkedIn: [linkedin.com/in/juan-carlos-casava](https://www.linkedin.com/in/juan-carlos-casava)
