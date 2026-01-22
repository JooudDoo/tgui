"""Screens for the tgui Textual UI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from tgui.telegram.client import MessageEnvelope
from tgui.ui.widgets import ChatList, MenuPanel, MessageComposer, MessagePane, PanelLayout


class AuthScreen(Screen[None]):
    """Login screen for Telegram authentication."""

    BINDINGS = [
        ("escape", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the authentication screen.

        Returns
        -------
        ComposeResult
            Screen widgets for authentication.
        """
        yield Header(show_clock=True)
        with Vertical(id="auth-form"):
            yield Static("Telegram login", classes="panel-title")
            yield Input(placeholder="Phone number", id="auth-phone")
            yield Input(placeholder="Login code", id="auth-code")
            yield Input(placeholder="2FA password (optional)", id="auth-password", password=True)
            yield Button("Login", id="auth-login")
            yield Button("Settings", id="auth-settings")
        yield Footer()


class SettingsScreen(Screen[None]):
    """Settings screen for Telegram API credentials."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the settings screen.

        Returns
        -------
        ComposeResult
            Screen widgets for settings.
        """
        yield Header(show_clock=True)
        with Vertical(id="settings-form"):
            yield Static("Telegram settings", classes="panel-title")
            yield Input(placeholder="API ID", id="settings-api-id")
            yield Input(placeholder="API Hash", id="settings-api-hash")
            yield Input(placeholder="Session name", id="settings-session")
            yield Button("Save", id="settings-save")
            yield Button("Cancel", id="settings-cancel")
        yield Footer()


class ChatScreen(Screen[None]):
    """Main chat screen with chat list and messages."""

    def __init__(self) -> None:
        """Initialize the chat screen widgets."""
        super().__init__()
        self.chat_list = ChatList(id="chat-list")
        self.message_pane = MessagePane()

    def compose(self) -> ComposeResult:
        """Compose the chat screen layout.

        Returns
        -------
        ComposeResult
            Screen widgets for chat layout.
        """
        yield Header(show_clock=True)
        with Vertical(id="chat-screen"):
            yield MenuPanel(id="menu-panel")
            yield PanelLayout(self.chat_list, self.message_pane)
            yield MessageComposer(id="composer")
        yield Footer()

    def update_messages(self, message: MessageEnvelope) -> None:
        """Append a message to the message pane.

        Parameters
        ----------
        message : MessageEnvelope
            Message to display.
        """
        self.message_pane.append_message(message)
