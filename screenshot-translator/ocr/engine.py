from __future__ import annotations

import numpy as np
import easyocr


class OCREngine:
    def __init__(self, lang: str = "en") -> None:
        self._reader = easyocr.Reader([lang])

    def recognize(self, image: "np.ndarray | Image.Image") -> list[dict]:
        """Extract text blocks from an image.

        Args:
            image: numpy array (HxWxC RGB) or PIL Image.

        Returns:
            List of dicts with keys: text, bbox, confidence.
            bbox is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] in pixel coordinates.
        """
        if hasattr(image, "convert"):
            img_array = np.array(image.convert("RGB"))
        elif isinstance(image, np.ndarray):
            img_array = image
        else:
            raise TypeError(f"Expected PIL Image or ndarray, got {type(image)}")

        results = self._reader.readtext(img_array)
        if not results:
            return []

        blocks: list[dict] = []
        for bbox, text, confidence in results:
            blocks.append({
                "text": text.strip(),
                "bbox": bbox,
                "confidence": confidence,
            })
        return blocks
