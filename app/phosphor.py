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

# File:        phosphor.py
# Version:     1.0
# Author:      Michael Gasche
# Created:     2026-01
# Product:     Phosphor
# Description: Main application entry point for the Phosphor video player.


import locale
locale.setlocale(locale.LC_NUMERIC, "C")

import sys
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def run():
    app = QApplication(sys.argv)

    # Dark palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(33, 33, 33))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Highlight, QColor(90, 130, 255))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

    # Apply dark palette
    app.setPalette(dark_palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    run()
