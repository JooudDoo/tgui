"""Textual application shell for tgui."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static


class TguiApp(App[None]):
    """Main Textual application shell.

    Notes
    -----
    This is a minimal placeholder UI to validate packaging and rendering.
    It will be expanded with chat lists, message views, and input widgets.
    """

    CSS = """
    Screen {
        layout: vertical;
    }

    .body {
        height: 1fr;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the initial UI layout.

        Returns
        -------
        ComposeResult
            The Textual compose generator for this screen.
        """
        yield Header(show_clock=True)
        yield Static(
            "tgui is bootstrapped. Next step: Telegram auth + UI layout.",
            classes="body",
        )
        yield Footer()
