"""Image decoding helpers for terminal rendering."""

from __future__ import annotations

from PIL import Image


def open_image(path: str) -> Image.Image:
    """Open an image for rendering in the terminal.

    Parameters
    ----------
    path : str
        Path to the image file.

    Returns
    -------
    PIL.Image.Image
        Decoded image handle.
    """
    return Image.open(path)
