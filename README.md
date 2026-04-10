# Teleprompter OBS

Custom Python teleprompter designed for OBS recording, focused on reducing eye movement and improving delivery when presenting or recording content.

---

## Problem

When recording videos or presentations, reading from a script often leads to:

* unnatural eye movement
* loss of flow while speaking
* constant switching between windows

Most available solutions are either hardware-based, expensive, or not well adapted to OBS workflows.

---

## Solution

This project provides a lightweight teleprompter implemented in Python with:

* a centered reading window
* smooth automatic scrolling
* keyboard-based control
* a configurable interface via JSON

It is designed to work alongside OBS without disrupting the recording workflow.

---

## Features

* Adjustable reading window
* Narrow text layout for better focus
* Optional ghost mode (dimmed surrounding area)
* Guide line for consistent pacing
* Scroll speed control
* Dynamic font size adjustment
* Optional status bar with auto-hide

---

## How it works

The application is built using:

* `tkinter` for the interface
* a canvas-based rendering system for text
* an event loop (`after`) for smooth scrolling

The “ghost mode” uses layered drawing and dimmed regions to guide focus toward a central reading area.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/jcastorena92/teleprompter-obs.git
cd teleprompter-obs
```

Create a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate
```

No external dependencies are required.

---

## Usage

```bash
python teleprompter.py --file path/to/script.txt --config config_obs.json
```

Example:

```bash
python teleprompter.py --file guion.txt --config config_obs.json
```

---

## Controls

* Space: start / pause
* Up / Down: adjust speed
* PageUp / PageDown: manual scroll
* + / -: adjust font size
* r: reset position
* Esc: exit

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

* video recording
* academic presentations
* voice-over work
* script-based delivery

---

## Author

Juan Carlos Castorena Avalos

Background in engineering, currently transitioning into translation and technical tooling.

---

## License

MIT License © 2026 Juan Carlos Castorena Avalos

---


## Notes

This project was built to solve a practical workflow problem: recording structured content while maintaining a natural delivery.

It is part of a broader interest in building tools for language and content workflows.
