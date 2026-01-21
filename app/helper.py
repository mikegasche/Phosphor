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

# File:        helper.py
# Version:     1.0
# Author:      Michael Gasche
# Created:     2026-01
# Product:     Phosphor
# Description: Helper functions for the Phosphor video player.


import os
import sys


def get_resource_path(filename: str) -> str:
    if getattr(sys, "frozen", False):
        # Path in the bundled PyInstaller build
        if sys.platform == "darwin":
            # macOS app bundle: Resources are located in Contents/Resources
            base_path = os.path.join(sys._MEIPASS, "..", "Resources", "resources")
        else:
            # Windows or Linux: directly in the temporary folder
            base_path = os.path.join(sys._MEIPASS, "resources")
        base_path = os.path.abspath(base_path)
    else:
        # Development: relative paths
        base_path = os.path.join(os.path.dirname(__file__), "resources")
    
    return os.path.join(base_path, filename)
