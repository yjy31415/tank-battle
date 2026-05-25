from __future__ import annotations

import io

from PIL import Image, ImageDraw, ImageFont
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFileDialog, QApplication,
)

OVERLAY_FONT_SIZE = 13
OVERLAY_PADDING = 4


def _get_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ["msyh.ttc", "simhei.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(name, OVERLAY_FONT_SIZE)
        except OSError:
            continue
    return ImageFont.load_default()


def _render_overlay(
    image: Image.Image,
    translations: list[dict],
    display_mode: str = "bilingual",
) -> Image.Image:
    """Draw translated text over the original image."""
    img = image.copy().convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = _get_font()

    overlay_color = (255, 255, 255, 230)
    original_color = (80, 80, 80, 255)
    translated_color = (220, 50, 50, 255)

    for item in translations:
        bbox = item["bbox"]
        original = item["original"]
        translated = item["translated"]

        x1 = int(min(p[0] for p in bbox))
        y1 = int(min(p[1] for p in bbox))
        box_w = int(max(p[0] for p in bbox) - x1)
        box_h = int(max(p[1] for p in bbox) - y1)

        if display_mode == "bilingual":
            total_h = box_h * 2 + OVERLAY_PADDING * 3
            draw.rectangle(
                [x1 - OVERLAY_PADDING, y1 - OVERLAY_PADDING,
                 x1 + box_w + OVERLAY_PADDING, y1 + total_h],
                fill=overlay_color,
            )
            draw.text((x1, y1), original, fill=original_color, font=font)
            draw.text((x1, y1 + box_h + OVERLAY_PADDING),
                      translated, fill=translated_color, font=font)
        else:
            total_h = box_h + OVERLAY_PADDING * 2
            draw.rectangle(
                [x1 - OVERLAY_PADDING, y1 - OVERLAY_PADDING,
                 x1 + box_w + OVERLAY_PADDING, y1 + total_h],
                fill=overlay_color,
            )
            draw.text((x1, y1), translated, fill=translated_color, font=font)

    return img.convert("RGB")


class ResultWindow(QWidget):
    def __init__(
        self,
        pil_image: Image.Image,
        translations: list[dict],
        display_mode: str = "bilingual",
    ) -> None:
        super().__init__()
        self.setWindowTitle("翻译结果")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.resize(900, 650)

        self._pil_image = pil_image
        self._translations = translations
        self._display_mode = display_mode

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        scroll = QScrollArea()
        scroll.setAlignment(Qt.AlignCenter)
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignCenter)
        scroll.setWidget(self._image_label)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()

        copy_btn = QPushButton("复制译文")
        copy_btn.clicked.connect(self._copy)
        btn_layout.addWidget(copy_btn)

        save_btn = QPushButton("保存图片")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        self._render()

    def _render(self) -> None:
        rendered = _render_overlay(self._pil_image, self._translations, self._display_mode)
        buffer = io.BytesIO()
        rendered.save(buffer, format="PNG")
        qimg = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(
            self._image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "_image_label") and self._image_label.pixmap():
            self._render()

    def _copy(self) -> None:
        text = "\n".join(
            f"{t['original']}\n{t['translated']}"
            for t in self._translations
        )
        QApplication.clipboard().setText(text)

    def _save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "保存图片", "translated.png", "PNG (*.png)"
        )
        if path:
            rendered = _render_overlay(
                self._pil_image, self._translations, self._display_mode
            )
            rendered.save(path, format="PNG")
