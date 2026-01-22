"""Application entrypoint for tgui."""

from __future__ import annotations

from tgui.ui.app import TguiApp


def run() -> None:
    """Run the Textual application.

    Returns
    -------
    None
        This function runs the UI loop and exits when the app is closed.
    """
    app = TguiApp()
    app.run()
