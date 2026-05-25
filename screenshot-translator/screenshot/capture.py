from __future__ import annotations

import mss
from PIL import Image


def capture_region(left: int, top: int, width: int, height: int) -> Image.Image:
    """Capture a screen region and return as PIL Image (RGB)."""
    with mss.MSS() as sct:
        monitor = {"top": top, "left": left, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
