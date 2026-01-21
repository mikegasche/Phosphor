# ------------------------------------------------------------------------------
# Copyright (c) 2026 Michael Gasche
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ------------------------------------------------------------------------------

# File:        mpv_player.py
# Version:     1.0
# Author:      Michael Gasche
# Created:     2026-01
# Product:     Phosphor
# Description: MPV video player wrapper with shader and audio effects.


import mpv
import platform
import threading
from pathlib import Path

from helper import get_resource_path


# -------------------------------
# MPVPlayer class
# -------------------------------

class MPVPlayer:
    def __init__(self, wid: int = None, retro_audio: bool = False, osc: bool = True, main_window=None, settings=None):
        """Initialize MPV wrapper; MPV instance created on video load."""

        self.main_window = main_window
        self.settings = settings
        self._crt_enabled = False
        self._scanlines_enabled = False
        self._vhs_enabled = False
        self._retro_audio_enabled = retro_audio
        self._file_loaded = False
        self._lock = threading.Lock()
        self._terminated = False

        # shader stage levels (-5 .. +5), UI controlled
        self.shader_levels = {
            "crt": 0,
            "scanlines": 0,
            "vhs": 0,
        }

        # MPV creation kwargs
        self._mpv_kwargs = dict(
            osc=osc,
            hwdec="no",
            input_builtin_bindings=True,
            input_default_bindings=True,
            input_vo_keyboard=True,
            log_handler=self.mpv_log,
            loglevel="warn",
        )

        if wid is not None:
            self._mpv_kwargs["wid"] = str(wid)
            self._mpv_kwargs["vo"] = "opengl"
        else:
            self._mpv_kwargs["vo"] = "gpu"

        # Apply retro audio filter ONLY at creation
        if self._retro_audio_enabled:
            self._mpv_kwargs["af"] = f"lavfi=[{self._get_audio_filter()}]"

        self.mpv = None


    # -------------------------------
    # Internal: create MPV instance
    # -------------------------------

    def _create_mpv(self):
        """Instantiate MPV object if not already created."""
        if self.mpv is None:
            self.mpv = mpv.MPV(**self._mpv_kwargs)
            self.mpv.keep_open = True
            self.mpv.pause = True
            self.mpv.observe_property("file-loaded", self._on_file_loaded)

            self.mpv.input_default_bindings = True
            self.mpv.input_vo_keyboard = True


    # -------------------------------
    # Logging
    # -------------------------------

    def mpv_log(self, level, component, message):
        """Simple logging for MPV messages."""
        print(f"[MPV {level}][{component}] {message}", flush=True)


    # -------------------------------
    # Effect toggles
    # -------------------------------

    def enable_crt(self, enabled: bool):
        self._crt_enabled = enabled
        self._update_shaders()

    def enable_scanlines(self, enabled: bool):
        self._scanlines_enabled = enabled
        self._update_shaders()

    def enable_vhs(self, enabled: bool):
        self._vhs_enabled = enabled
        self._update_shaders()


    # -------------------------------
    # Shader stage selection
    # -------------------------------

    def set_shader_level(self, shader: str, level: float):
        """
        Set shader stage from slider (-5..+5).
        Stage is always loaded, visibility controlled by enabled flags.
        """
        level_i = int(round(level))
        level_i = max(-5, min(5, level_i))
        self.shader_levels[shader] = level_i
        self._update_shaders()


    # -------------------------------
    # Update GLSL shaders
    # -------------------------------

    def _update_shaders(self):
        """
        Load GLSL shader FILES based on:
        - enabled flags
        - integer shader stage (-5..+5)
        """
        if not self.mpv:
            return

        shaders = []

        if self._crt_enabled:
            lvl = self.shader_levels["crt"]
            f = Path(get_resource_path(f"shaders/crt_base_{lvl}.glsl"))
            if f.exists():
                shaders.append(str(f))

        if self._scanlines_enabled:
            lvl = self.shader_levels["scanlines"]
            f = Path(get_resource_path(f"shaders/scanlines_{lvl}.glsl"))
            if f.exists():
                shaders.append(str(f))

        if self._vhs_enabled:
            lvl = self.shader_levels["vhs"]
            f = Path(get_resource_path(f"shaders/vhs_noise_{lvl}.glsl"))
            if f.exists():
                shaders.append(str(f))

        self.mpv.glsl_shaders = shaders

        if not shaders:
            print("No shaders loaded (all disabled or files missing)", flush=True)


    # -------------------------------
    # Retro Audio
    # -------------------------------

    def enable_retro_audio(self, enabled: bool):
        """Enable or disable retro audio."""
        self._retro_audio_enabled = enabled


    # -------------------------------
    # Load video
    # -------------------------------

    def load(self, path: str):
        """Load a video file into MPV, handling missing installation or library path issues."""
        self._file_loaded = False

        try:
            self._create_mpv()
        except Exception as e:
            # MPV could not be instantiated → MPV is probably missing or paths are not set
            msg = "Failed to initialize MPV.\n\n"
            system = platform.system()
            if system == "Darwin":
                msg += (
                    "Make sure MPV is installed (e.g., via Homebrew) and that DYLD_LIBRARY_PATH includes its libraries.\n\n"
                    "You can test in Terminal:\n"
                    "  echo $DYLD_LIBRARY_PATH\n"
                    "  mpv --version"
                )
            elif system == "Linux":
                msg += (
                    "Make sure MPV is installed and LD_LIBRARY_PATH (or PATH) includes its libraries.\n\n"
                    "Test in Terminal:\n"
                    "  echo $LD_LIBRARY_PATH\n"
                    "  mpv --version"
                )
            elif system == "Windows":
                msg += (
                    "Make sure MPV is installed and the folder containing mpv.exe is in your PATH."
                )
            else:
                msg += "Make sure MPV is installed and available in your system PATH."

            if self.main_window:
                self.main_window.show_error("MPV Initialization Error", msg)
            return

        # Load video
        if self.mpv and not self._terminated:
            try:
                self.mpv.command("loadfile", path, "replace")
                self.mpv.pause = False
            except Exception as e:
                if self.main_window:
                    self.main_window.show_error("Error Loading Video", f"Error loading file:\n{e}")


    # -------------------------------
    # Play / Pause
    # -------------------------------

    def toggle_pause(self):
        """Toggle pause/play."""
        if self.mpv:
            self.mpv.pause = not self.mpv.pause


    # -------------------------------
    # Stop / Terminate
    # -------------------------------

    def terminate(self):
        """Terminate MPV safely."""
        def _terminate():
            with self._lock:
                if self.mpv:
                    try:
                        # Remove observers first
                        self.mpv.unobserve_property("file-loaded", self._on_file_loaded)
                    except Exception:
                        pass
                    try:
                        self.mpv.terminate()
                        self._terminated = True
                    except Exception:
                        pass
                    self.mpv = None

        threading.Thread(target=_terminate, daemon=True).start()


    # -------------------------------
    # Events
    # -------------------------------

    def _on_file_loaded(self, name, val):
        """Callback when MPV finishes loading a file."""
        if not self.mpv or self._terminated:
            return
        self._file_loaded = bool(val)
        if self._file_loaded:
            self._update_shaders()

    def _mpv_event(self, event):
        if event["event_id"] == mpv.MPV_EVENT_SHUTDOWN:
            self.terminate()


    # -------------------------------
    # Retro Audio filter
    # -------------------------------

    def _get_audio_filter(self):
        """Retro Audio mit leichtem Mono, Kompressor + Make-up, Bitcrush und Echo."""
        return ",".join([
            "highpass=f=150",
            "lowpass=f=6000",
            "acompressor=threshold=0.2:ratio=3:makeup=6",
            "acrusher=bits=8",
            "pan=stereo|c0=0.7*c0+0.3*c1|c1=0.7*c1+0.3*c0",
            "aecho=0.05:0.3:1:0.3"
        ])
