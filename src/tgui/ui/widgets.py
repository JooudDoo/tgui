"""Custom Textual widgets for tgui."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, OptionList, Static

from tgui.telegram.client import ChatSummary, MessageEnvelope


class MenuPanel(Static):
    """Simple menu panel with common actions."""

    def compose(self) -> ComposeResult:
        """Compose menu actions.

        Returns
        -------
        ComposeResult
            Child widgets for the menu panel.
        """
        yield Button("Refresh", id="menu-refresh")
        yield Button("Settings", id="menu-settings")
        yield Button("Quit", id="menu-quit")


class ChatList(OptionList):
    """Option list for available chats."""

    def __init__(self, **kwargs: object) -> None:
        """Initialize the chat list widget.

        Parameters
        ----------
        **kwargs : object
            Keyword arguments passed to OptionList.
        """
        super().__init__(**kwargs)
        self._chat_ids: list[int] = []

    def set_chats(self, chats: list[ChatSummary]) -> None:
        """Replace the chat list options.

        Parameters
        ----------
        chats : list[ChatSummary]
            Chat summaries to display.
        """
        self.clear_options()
        self._chat_ids = []
        for chat in chats:
            label = chat.title or f"Chat {chat.chat_id}"
            self.add_option(label)
            self._chat_ids.append(chat.chat_id)

    def chat_id_for_index(self, index: int) -> int | None:
        """Return a chat id for an option index.

        Parameters
        ----------
        index : int
            Option index from the list.

        Returns
        -------
        int | None
            Chat id for the index, if available.
        """
        if 0 <= index < len(self._chat_ids):
            return self._chat_ids[index]
        return None


class MessagePane(Static):
    """Scrollable message view pane."""

    def __init__(self) -> None:
        """Initialize the message pane."""
        super().__init__("")
        self._lines: list[str] = []

    def append_message(self, message: MessageEnvelope) -> None:
        """Append a message to the pane.

        Parameters
        ----------
        message : MessageEnvelope
            Message data to render.
        """
        sender = message.sender_id if message.sender_id is not None else "me"
        self._lines.append(f"{sender}: {message.text}")
        self.update("\n".join(self._lines))

    def clear_messages(self) -> None:
        """Clear all rendered messages."""
        self._lines = []
        self.update("")


class MessageComposer(Static):
    """Message input and send controls."""

    def compose(self) -> ComposeResult:
        """Compose the message composer widgets.

        Returns
        -------
        ComposeResult
            Child widgets for the composer.
        """
        with Horizontal():
            yield Input(placeholder="Type a message", id="message-input")
            yield Button("Send", id="message-send")


class PanelLayout(Static):
    """Composite layout for chats and messages."""

    def __init__(self, chat_list: ChatList, message_pane: MessagePane) -> None:
        """Initialize the panel layout.

        Parameters
        ----------
        chat_list : ChatList
            Chat list widget instance.
        message_pane : MessagePane
            Message pane widget instance.
        """
        super().__init__()
        self._chat_list = chat_list
        self._message_pane = message_pane

    def compose(self) -> ComposeResult:
        """Compose the main panel layout.

        Returns
        -------
        ComposeResult
            Child widgets for the panel layout.
        """
        with Horizontal():
            with Vertical(id="chat-column"):
                yield Static("Chats", classes="panel-title")
                yield self._chat_list
            with Vertical(id="message-column"):
                yield Static("Messages", classes="panel-title")
                yield self._message_pane
