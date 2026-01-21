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

# File:        main_window.py
# Version:     1.0
# Author:      Michael Gasche
# Created:     2026-01
# Product:     Phosphor
# Description: c


import os
import sys
import json
import platform

from threading import Thread

from helper import get_resource_path
from player.mpv_player import MPVPlayer

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSizePolicy,
    QVBoxLayout,
    QWidget
)

ON_SCREEN_CONTROLLER = True
if not ON_SCREEN_CONTROLLER:
    from PySide6.QtGui import QKeySequence, QShortcut


# --------------------------------------------------------------
# App constants
# --------------------------------------------------------------

# App title and version
APP_NAME = "Phosphor"
APP_VERSION = "1.0"
FULL_TITLE = f"{APP_NAME} {APP_VERSION}"

# Presets Definition
PRESETS = {
    "Clean":      {"crt": False, "scan": False, "vhs": False},
    "80s TV":     {"crt": True,  "scan": True,  "vhs": False},
    "VHS (later)": {"crt": True,  "scan": True,  "vhs": True}
}
CUSTOM_PRESET_NAME = "Custom"

# Shader Stage Files
CRT_STAGES = {i: get_resource_path(f"shaders/crt_base_{i}.glsl") for i in range(-5, 6)}
SCANLINE_STAGES = {i: get_resource_path(f"shaders/scanlines_{i}.glsl") for i in range(-5, 6)}
VHS_STAGES = {i: get_resource_path(f"shaders/vhs_noise_{i}.glsl") for i in range(-5, 6)}

# Map shader names from UI to MPVPlayer keys
SHADER_KEY_MAP = {
    "CRT Shader": "crt",
    "Scanline Shader": "scanlines",
    "VHS Shader": "vhs"
}


# --------------------------------------------------------------
# MainWindow class
# --------------------------------------------------------------

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setup_menu()

        self.setWindowTitle(FULL_TITLE)
        self.setWindowIcon(QIcon(get_resource_path("app_icon.png")))
        self.resize(300, 526)
        self.setFixedSize(300, 526)
        self.setWindowFlags(Qt.Window)
        self.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.04);
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.08);
                border-radius: 6px;
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.15);
            }
            """)

        # ---------------- Sidebar ----------------
        frame = QFrame(self)
        frame.setFrameShape(QFrame.NoFrame)
        frame.setStyleSheet("QFrame { border: none; }")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop)

        # Image
        hbox_title = QHBoxLayout()
        hbox_title.setContentsMargins(0, 0, 0, 0)
        hbox_title.setSpacing(0)
        title_img_path = get_resource_path("label.png")
        if os.path.exists(title_img_path):
            pixmap = QPixmap(title_img_path)
            title_icon = QLabel()
            title_icon.setPixmap(pixmap)
            title_icon.setScaledContents(True)
            title_icon.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            hbox_title.addWidget(title_icon)

        layout.addLayout(hbox_title)

        layout_control = QVBoxLayout()
        layout_control.setContentsMargins(12, 12, 12, 12)
        layout_control.setSpacing(8)

        layout_control.addSpacing(12)

        # Video controls
        self.is_paused = True
        BTN_SIZE = 64
        ICON_PADDING = 14
        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)
        controls_row.addStretch(10)
        self.open_btn = QPushButton()
        self.open_btn.setFixedSize(BTN_SIZE, BTN_SIZE)
        self.open_btn.setIcon(QPixmap(get_resource_path("open.png")))
        self.open_btn.setIconSize(QSize(
            BTN_SIZE - ICON_PADDING,
            BTN_SIZE - ICON_PADDING
        ))
        self.open_btn.setFlat(True)
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(BTN_SIZE, BTN_SIZE)
        self.play_btn.setFlat(True)
        self.play_icon = QPixmap(get_resource_path("play.png"))
        self.pause_icon = QPixmap(get_resource_path("pause.png"))
        self.play_btn.setIcon(self.play_icon)
        self.play_btn.setIconSize(QSize(
            BTN_SIZE - ICON_PADDING,
            BTN_SIZE - ICON_PADDING
        ))
        controls_row.addWidget(self.open_btn)
        controls_row.addStretch(1)
        controls_row.addWidget(self.play_btn)
        controls_row.addStretch(10)
        layout_control.addLayout(controls_row)
        layout_control.addSpacing(16)

        # Shader sliders
        layout_control.addWidget(QLabel("CRT Shader Strength"))
        self.crt_slider = QSlider(Qt.Horizontal)
        self.crt_slider.setMinimum(-5)
        self.crt_slider.setMaximum(5)
        self.crt_slider.setTickInterval(1)
        self.crt_slider.setTickPosition(QSlider.TicksBelow)
        layout_control.addWidget(self.crt_slider)

        layout_control.addWidget(QLabel("Scanline Shader Strength"))
        self.scan_slider = QSlider(Qt.Horizontal)
        self.scan_slider.setMinimum(-5)
        self.scan_slider.setMaximum(5)
        self.scan_slider.setTickInterval(1)
        self.scan_slider.setTickPosition(QSlider.TicksBelow)
        layout_control.addWidget(self.scan_slider)

        layout_control.addWidget(QLabel("VHS Shader Strength"))
        self.vhs_slider = QSlider(Qt.Horizontal)
        self.vhs_slider.setMinimum(-5)
        self.vhs_slider.setMaximum(5)
        self.vhs_slider.setTickInterval(1)
        self.vhs_slider.setTickPosition(QSlider.TicksBelow)
        layout_control.addWidget(self.vhs_slider)
        layout_control.addSpacing(8)

        # Preset selector
        layout_control.addWidget(QLabel("Preset"))
        self.preset_box = QComboBox()
        self.preset_box.addItems(["Clean", "80s TV", "VHS (later)"])
        layout_control.addWidget(self.preset_box)
        layout_control.addSpacing(2)

        # Effect checkboxes
        self.crt_cb = QCheckBox("CRT Frame")
        self.scan_cb = QCheckBox("Scanlines")
        self.vhs_cb = QCheckBox("VHS Noise")
        self.crt_cb.toggled.connect(self.update_preset_combobox)
        self.scan_cb.toggled.connect(self.update_preset_combobox)
        self.vhs_cb.toggled.connect(self.update_preset_combobox)
        self.audio_cb = QCheckBox("Retro Audio (set before loading)")
        checkbox_layout = QVBoxLayout()
        checkbox_layout.setContentsMargins(4, 0, 0, 0)
        checkbox_layout.setSpacing(8)
        checkbox_layout.addWidget(self.crt_cb)
        checkbox_layout.addWidget(self.scan_cb)
        checkbox_layout.addWidget(self.vhs_cb)
        checkbox_layout.addWidget(self.audio_cb)
        layout_control.addLayout(checkbox_layout)

        layout.addLayout(layout_control)

        self.setContentsMargins(0, 0, 0, 0)

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

        self.setCentralWidget(frame)
        self.show()

        # ---------------- Player ----------------
        self.player = None
        self.retro_audio_enabled = False

        # ---------------- Connect signals ----------------
        self.open_btn.clicked.connect(self.open_file)
        self.play_btn.clicked.connect(self.toggle_play)
        self.crt_cb.toggled.connect(self.on_crt_toggled)
        self.scan_cb.toggled.connect(self.on_scan_toggled)
        self.vhs_cb.toggled.connect(self.on_vhs_toggled)
        self.audio_cb.toggled.connect(self.on_audio_toggled)
        self.crt_slider.valueChanged.connect(lambda val: self.on_shader_slider_change("CRT Shader", val))
        self.scan_slider.valueChanged.connect(lambda val: self.on_shader_slider_change("Scanline Shader", val))
        self.vhs_slider.valueChanged.connect(lambda val: self.on_shader_slider_change("VHS Shader", val))
        self.preset_box.currentIndexChanged.connect(self.on_preset_changed)

        # ---------------- Settings ----------------
        self.settings_file = self._get_settings_file()
        self.last_dir = ""
        self.settings = {
            "last_dir": "",
            "crt_cb": False,
            "scan_cb": False,
            "vhs_cb": False,
            "audio_cb": False,
            "crt_slider": 0,
            "scan_slider": 0,
            "vhs_slider": 0
        }
        self._load_settings()
        self._apply_settings_to_ui()

        # ---------------- Keyboard Shortcuts ----------------
        if not ON_SCREEN_CONTROLLER:
            QShortcut(QKeySequence("Space"), self, activated=self.toggle_play, context=Qt.ApplicationShortcut)
            QShortcut(QKeySequence("Right"), self, activated=lambda: self.player.mpv.command("seek", 10, "relative"), context=Qt.ApplicationShortcut)
            QShortcut(QKeySequence("Left"), self, activated=lambda: self.player.mpv.command("seek", -10, "relative"), context=Qt.ApplicationShortcut)
            QShortcut(QKeySequence("Up"), self, activated=lambda: self.player.mpv.command("add", "volume", 5), context=Qt.ApplicationShortcut)
            QShortcut(QKeySequence("Down"), self, activated=lambda: self.player.mpv.command("add", "volume", -5), context=Qt.ApplicationShortcut)
            QShortcut(QKeySequence("F"), self, activated=lambda: self.player.mpv.command("cycle", "fullscreen"), context=Qt.ApplicationShortcut)


    # --------------------------------------------------------------
    # Menu setup
    # --------------------------------------------------------------

    def create_action(self, name, func):
        action = QAction(name, self)
        action.triggered.connect(func)
        return action
    
    def setup_menu(self):
        menubar = self.menuBar()

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.create_action("About", self.show_about))

    def show_about(self):
        box = QMessageBox(self)
        box.setWindowTitle("About")
        
        icon_path = get_resource_path("app_icon.icns")
        if os.path.exists(icon_path):
            box.setIconPixmap(QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            box.setIcon(QMessageBox.Information)
        
        box.setText(f"{APP_NAME}\nVersion: {APP_VERSION}\n\n© 2026 Michael Gasche\nhttps://github.com/mikegasche\n\nAll rights reserved.")
        box.setStandardButtons(QMessageBox.Ok)
        box.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
            }
        """)
        
        box.exec()

    # --------------------------------------------------------------
    # Message Boxes
    # --------------------------------------------------------------

    def show_info(self, title: str, message: str):
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setText(message)
        box.setIconPixmap(QPixmap(self.resource_path("information.png")))
        box.exec()

    def show_warning(self, title: str, message: str):
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setText(message)
        box.setIconPixmap(QPixmap(self.resource_path("warning.png")))
        box.exec()

    def show_error(self, title: str, message: str):
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setText(message)
        box.setIconPixmap(QPixmap(self.resource_path("error.png")))
        box.exec()


    # --------------------------------------------------------------
    # Events
    # --------------------------------------------------------------

    def _on_video_widget_close(self, event):
        if self.player:
            self.player.terminate()
            self.player = None
        event.accept()

    def closeEvent(self, event):
        try:
            if self.player:
                self.player.terminate()
                self.player = None
        except Exception as e:
            self.show_error("Error", f"Close error:\n{e}")
        event.accept()

    if not ON_SCREEN_CONTROLLER:
        def keyPressEvent(self, event):
            if not self.player or not self.player.mpv:
                return
            key = event.key()
            if key == Qt.Key_Space:
                self.player.toggle_pause()
            elif key == Qt.Key_Right:
                self.player.mpv.command("seek", 10, "relative")
            elif key == Qt.Key_Left:
                self.player.mpv.command("seek", -10, "relative")
            elif key == Qt.Key_Up:
                self.player.mpv.command("add", "volume", 5)
            elif key == Qt.Key_Down:
                self.player.mpv.command("add", "volume", -5)
            elif key == Qt.Key_F:
                self.player.mpv.command("cycle", "fullscreen")


    # --------------------------------------------------------------
    # UI Callbacks
    # --------------------------------------------------------------

    def toggle_play(self):
        if not self.player:
            return

        self.player.toggle_pause()
        self.is_paused = not self.is_paused

        if self.is_paused:
            self.play_btn.setIcon(self.play_icon)
        else:
            self.play_btn.setIcon(self.pause_icon)


    # --------------------------------------------------------------
    # Shader / Effect Callbacks
    # --------------------------------------------------------------

    def on_crt_toggled(self, enabled: bool):
        if self.player:
            self.player.enable_crt(enabled)
        self.settings["crt_cb"] = enabled
        self._save_settings()

    def on_scan_toggled(self, enabled: bool):
        if self.player:
            self.player.enable_scanlines(enabled)
        self.settings["scan_cb"] = enabled
        self._save_settings()

    def on_vhs_toggled(self, enabled: bool):
        if self.player:
            self.player.enable_vhs(enabled)
        self.settings["vhs_cb"] = enabled
        self._save_settings()

    def on_audio_toggled(self, enabled: bool):
        self.retro_audio_enabled = enabled
        if self.player:
            self.player.enable_retro_audio(enabled)
        self.settings["audio_cb"] = enabled
        self._save_settings()


    # --------------------------------------------------------------
    # Preset Management
    # --------------------------------------------------------------

    def update_preset_combobox(self):
        current_state = {
            "crt": self.crt_cb.isChecked(),
            "scan": self.scan_cb.isChecked(),
            "vhs": self.vhs_cb.isChecked()
        }

        for preset_name, preset_state in PRESETS.items():
            if current_state == preset_state:
                self.preset_box.setCurrentText(preset_name)
                return

        if CUSTOM_PRESET_NAME not in [self.preset_box.itemText(i) for i in range(self.preset_box.count())]:
            self.preset_box.addItem(CUSTOM_PRESET_NAME)
        self.preset_box.setCurrentText(CUSTOM_PRESET_NAME)


    # --------------------------------------------------------------
    # Change Handlers
    # --------------------------------------------------------------

    def on_shader_slider_change(self, shader_name, slider_value):
        """Select the corresponding static shader file based on slider value (-5..5)."""
        stage_files = {
            "CRT Shader": CRT_STAGES,
            "Scanline Shader": SCANLINE_STAGES,
            "VHS Shader": VHS_STAGES
        }
        file = stage_files[shader_name].get(slider_value, None)

        # Save the slider value in settings
        if shader_name == "CRT Shader":
            self.settings["crt_slider"] = slider_value
        elif shader_name == "Scanline Shader":
            self.settings["scan_slider"] = slider_value
        elif shader_name == "VHS Shader":
            self.settings["vhs_slider"] = slider_value
        self._save_settings()

        # ⚡ Apply the change to the player immediately
        if self.player:
            key = SHADER_KEY_MAP[shader_name]
            self.player.set_shader_level(key, slider_value)

    def on_preset_changed(self, index):
        preset_name = self.preset_box.currentText()
        if preset_name in PRESETS:
            state = PRESETS[preset_name]
            self.crt_cb.setChecked(state["crt"])
            self.scan_cb.setChecked(state["scan"])
            self.vhs_cb.setChecked(state["vhs"])


    # --------------------------------------------------------------
    # File Operations
    # --------------------------------------------------------------

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Open Video", self.last_dir or "", "Videos (*.mp4 *.mkv *.avi *.mov)"
        )
        if file:
            self._open_video_file(file)

    def _open_video_file(self, file):
        """Open a video file and initialize MPV player with static shader files (-5..+5 stages)."""
        self.audio_cb.setEnabled(False)
        
        if self.player:
            self.player.terminate()
            self.player = None
        QApplication.processEvents()

        # macOS: do not create empty Qt window, embed not supported
        if platform.system() == "Darwin":
            self.player = MPVPlayer(
                wid=None,  # no embedding
                retro_audio=self.audio_cb.isChecked(),
                osc=ON_SCREEN_CONTROLLER,
                main_window=self,
                settings=self.settings
            )
        else:
            # Linux/Windows: optional QWidget embedding
            self.mpv_window = QWidget()
            self.mpv_window.setWindowTitle("PHOSPHOR Video")
            self.mpv_window.setGeometry(100, 100, 800, 450)
            self.mpv_window.show()
            QApplication.processEvents()

            self.player = MPVPlayer(
                wid=int(self.mpv_window.winId()),
                retro_audio=self.audio_cb.isChecked(),
                osc=ON_SCREEN_CONTROLLER
            )

        # ---------------- Apply checkbox activation first ----------------
        self.player.enable_crt(self.settings.get("crt_cb", False))
        self.player.enable_scanlines(self.settings.get("scan_cb", False))
        self.player.enable_vhs(self.settings.get("vhs_cb", False))
        self.player.enable_retro_audio(self.settings.get("audio_cb", False))

        # Save last directory
        self.last_dir = os.path.dirname(file)
        self.settings["last_dir"] = self.last_dir
        self._save_settings()

        def load_and_apply_shaders():
            # ---------------- Load video last ----------------
            self.player.load(file)
            self.is_paused = False
            self.play_btn.setIcon(self.pause_icon)
            QApplication.processEvents()
            # ---------------- Preload shaders according to slider values ----------------
            # ⚡ Important: call on_shader_slider_change AFTER enabling checkboxes
            self.on_shader_slider_change("CRT Shader", self.settings.get("crt_slider", 0))
            self.on_shader_slider_change("Scanline Shader", self.settings.get("scan_slider", 0))
            self.on_shader_slider_change("VHS Shader", self.settings.get("vhs_slider", 0))

        Thread(target=load_and_apply_shaders, daemon=True).start()


    # --------------------------------------------------------------
    # Settings Management
    # --------------------------------------------------------------

    def _get_settings_file(self):
        home = os.path.expanduser("~")
        if sys.platform == "darwin":
            base = os.path.join(home, "Library", "Application Support", "Phosphor")
        elif os.name == "nt":
            base = os.path.join(os.environ.get("APPDATA", home), "Phosphor")
        else:
            base = os.path.join(home, ".Phosphor")

        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "settings.json")

    def _load_settings(self):
        try:
            with open(self.settings_file, "r") as f:
                data = json.load(f)
                self.settings.update(data)
                self.last_dir = self.settings.get("last_dir", "")
        except Exception:
            pass

    def _apply_settings_to_ui(self):
        """Apply loaded settings to checkboxes and sliders."""
        self.crt_cb.setChecked(self.settings.get("crt_cb", False))
        self.scan_cb.setChecked(self.settings.get("scan_cb", False))
        self.vhs_cb.setChecked(self.settings.get("vhs_cb", False))
        self.audio_cb.setChecked(self.settings.get("audio_cb", False))
        self.crt_slider.setValue(self.settings.get("crt_slider", 0))
        self.scan_slider.setValue(self.settings.get("scan_slider", 0))
        self.vhs_slider.setValue(self.settings.get("vhs_slider", 0))

        self.update_preset_combobox()

    def _save_settings(self):
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f)
        except Exception:
            pass
