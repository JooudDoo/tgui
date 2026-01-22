"""Textual application shell for tgui."""

from __future__ import annotations

import os
from dataclasses import dataclass

from textual.app import App
from textual.widgets import Button, Input, OptionList

from tgui.core.settings import AppSettings, load_settings
from tgui.core.state import AppState
from tgui.telegram.client import MessageEnvelope, TelegramService
from tgui.ui.screens import AuthScreen, ChatScreen, SettingsScreen


@dataclass
class AuthPayload:
    """Payload for auth requests.

    Attributes
    ----------
    phone : str
        Phone number for login.
    code : str
        Login code provided by Telegram.
    password : str
        Two-factor authentication password.
    """

    phone: str
    code: str
    password: str


class TguiApp(App[None]):
    """Main Textual application shell."""

    SCREENS = {
        "auth": AuthScreen,
        "settings": SettingsScreen,
        "chat": ChatScreen,
    }
    DEFAULT_SCREEN = "auth"

    CSS = """
    Screen {
        layout: vertical;
    }

    #auth-form, #settings-form {
        padding: 1 2;
        height: auto;
        width: 70%;
        margin: 2 4;
        background: $panel;
    }

    #chat-screen {
        height: 1fr;
    }

    #menu-panel {
        height: auto;
        layout: horizontal;
        padding: 0 1;
        background: $panel;
    }

    #chat-column {
        width: 35%;
        border: solid $panel;
        padding: 1;
    }

    #message-column {
        width: 65%;
        border: solid $panel;
        padding: 1;
    }

    .panel-title {
        text-style: bold;
        margin-bottom: 1;
    }

    #message-input {
        width: 1fr;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("s", "open_settings", "Settings"),
    ]

    def __init__(self) -> None:
        """Initialize the Textual application."""
        super().__init__()
        self.state = AppState()
        self._settings: AppSettings | None = None
        self._telegram: TelegramService | None = None

    def on_mount(self) -> None:
        """Initialize settings and show the first screen."""
        try:
            self._settings = load_settings(os.environ)
        except ValueError:
            self.switch_screen("settings")
            return

        self._telegram = TelegramService(self._settings.to_telegram_config())
        self.switch_screen("auth")

    def action_open_settings(self) -> None:
        """Open the settings screen."""
        self.switch_screen("settings")

    def action_refresh(self) -> None:
        """Refresh chat list from Telegram."""
        self.run_worker(self._refresh_dialogs())

    def _chat_screen(self) -> ChatScreen | None:
        screen = self.get_screen("chat")
        if isinstance(screen, ChatScreen):
            return screen
        return None

    async def _refresh_dialogs(self) -> None:
        if not self._telegram:
            return
        dialogs = await self._telegram.dialogs()
        self.state.chats = dialogs
        self.call_later(self._update_chat_list, dialogs)

    def _update_chat_list(self, dialogs: list) -> None:
        screen = self._chat_screen()
        if screen:
            screen.chat_list.set_chats(dialogs)

    def _handle_message(self, message: MessageEnvelope) -> None:
        screen = self._chat_screen()
        if screen:
            screen.update_messages(message)

    async def _authenticate(self, payload: AuthPayload) -> None:
        if not self._telegram:
            return

        def _code_callback() -> str:
            return payload.code

        await self._telegram.start(
            phone=payload.phone or None,
            code_callback=_code_callback,
            password=payload.password or None,
        )
        async def _on_message(message: MessageEnvelope) -> None:
            self.call_later(self._handle_message, message)

        self._telegram.add_message_listener(_on_message)
        self.call_later(self._show_chat)
        await self._refresh_dialogs()

    async def _dispatch_message(self, message: MessageEnvelope) -> None:
        self.call_later(self._handle_message, message)

    def _show_chat(self) -> None:
        if self.get_screen("chat") is None:
            self.switch_screen("chat")
        else:
            self.switch_screen("chat")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses from any screen."""
        button_id = event.button.id
        if button_id == "auth-login":
            payload = self._read_auth_payload()
            self.run_worker(self._authenticate(payload), exclusive=True)
            return
        if button_id == "auth-settings":
            self.switch_screen("settings")
            return
        if button_id == "settings-cancel":
            self.pop_screen()
            return
        if button_id == "settings-save":
            self._apply_settings()
            return
        if button_id == "menu-refresh":
            self.run_worker(self._refresh_dialogs())
            return
        if button_id == "menu-settings":
            self.switch_screen("settings")
            return
        if button_id == "menu-quit":
            self.exit()
            return
        if button_id == "message-send":
            self.run_worker(self._send_message())

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Update active chat selection."""
        screen = self._chat_screen()
        if not screen:
            return
        chat_id = screen.chat_list.chat_id_for_index(event.option_index)
        if chat_id is not None:
            self.state.active_chat_id = chat_id

    def _read_auth_payload(self) -> AuthPayload:
        screen = self.get_screen("auth")
        if not isinstance(screen, AuthScreen):
            return AuthPayload(phone="", code="", password="")
        phone = self.query_one("#auth-phone", Input).value
        code = self.query_one("#auth-code", Input).value
        password = self.query_one("#auth-password", Input).value
        return AuthPayload(phone=phone, code=code, password=password)

    def _apply_settings(self) -> None:
        api_id_raw = self.query_one("#settings-api-id", Input).value
        api_hash = self.query_one("#settings-api-hash", Input).value
        session_name = self.query_one("#settings-session", Input).value or "tgui"

        if not api_id_raw or not api_hash:
            return

        try:
            api_id = int(api_id_raw)
        except ValueError:
            return

        self._settings = AppSettings(api_id=api_id, api_hash=api_hash, session_name=session_name)
        self._telegram = TelegramService(self._settings.to_telegram_config())
        self.pop_screen()
        self.switch_screen("auth")

    async def _send_message(self) -> None:
        if not self._telegram or self.state.active_chat_id is None:
            return
        text = self.query_one("#message-input", Input).value
        if not text:
            return
        message = await self._telegram.send_message(self.state.active_chat_id, text)
        self.call_later(self._handle_message, message)
        self.call_later(self._clear_message_input)

    def _clear_message_input(self) -> None:
        input_box = self.query_one("#message-input", Input)
        input_box.value = ""
