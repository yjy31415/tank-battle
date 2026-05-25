from PIL import Image


def test_capture_region_returns_rgb_image():
    """Integration test: captures a tiny region of the primary monitor."""
    from screenshot.capture import capture_region

    img = capture_region(0, 0, 100, 100)
    assert isinstance(img, Image.Image)
    assert img.mode == "RGB"
    assert img.size == (100, 100)
