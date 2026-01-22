# Phosphor

<img src="app/resources/logo.png" width="200" height="200" alt="Phosphor Logo">

Phosphor is a retro video player for macOS and Windows that emulates the look and feel of CRT TVs, old VHS tapes, and classic scanlines. Designed for enthusiasts and developers who love vintage video effects.

> **Prerequisites:** Phosphor requires [MPV](https://mpv.io/) to be installed on your system.  
> - **macOS:** Install MPV via Homebrew (`brew install mpv`). The necessary libraries are automatically found by Phosphor.  
> - **Windows:** You need `libmpv-2.dll` (MPV executable is not required). A reliable source is [SourceForge MPV Windows builds](https://sourceforge.net/projects/mpv-player-windows/files/libmpv/). Ensure the folder containing `libmpv-2.dll` is in your system `PATH`.  

## Features

- Play video files (`.mp4`, `.mkv`, `.avi`, `.mov`) with a retro look.
- Adjustable shader effects:
  - **CRT Frame** – simulates old cathode-ray displays.
  - **Scanlines** – classic horizontal lines for retro visuals.
  - **VHS Noise** – adds VHS-style distortion and flicker.
- Single slider per shader to control effect strength (-5 to +5).
- Built-in presets: `Clean`, `80s TV`, `VHS (later)`.
- Custom preset support based on your slider settings.
- Optional **Retro Audio** filter for an authentic audio experience.
- Integrated On-Screen Controller (OSC) for mouse-based playback control.
- Mouse interactions (scroll, click, right-click) are fully supported.
- Cross-architecture macOS support (Intel & Apple Silicon).
- Persisted settings for last used directory, effect toggles, and slider values.

## Shaders

- **CRT Shader** – `shaders/crt_base_[−5..5].glsl`
- **Scanline Shader** – `shaders/scanlines_[−5..5].glsl`
- **VHS Shader** – `shaders/vhs_noise_[−5..5].glsl`
- Shaders are applied based on slider values. Negative and positive values select different pre-defined stages.

## Controls

- **Left-click** – Play / Pause (via OSC)  
- **Scroll wheel** – Seek or volume control depending on OSC mode  
- **Right-click** – Open OSC context menu  
- **Sliders & checkboxes** – Adjust shader strength and enable/disable effects  
- **Preset dropdown** – Quickly switch between predefined visual effects  

## Installation

1. Clone the repository:
   
   ```bash
   git clone https://github.com/mikegasche/phosphor.git
   cd phosphor
   ```

3. Set up Python environment:
   
   ```bash
   ./bin/setup.sh
   ```

4. Run the app:
   
   ```bash
   ./bin/phosphor.sh
   ```

## Building macOS App Bundle

   ```bash
   ./bin/make.sh
   ```

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
