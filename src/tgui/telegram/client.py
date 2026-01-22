"""Telegram integration powered by Telethon."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Awaitable, Callable, Iterable, Protocol

from telethon import TelegramClient, events

MessageHandler = Callable[["MessageEnvelope"], Awaitable[None]]


@dataclass(frozen=True)
class ChatSummary:
    """Summary metadata for a Telegram chat.

    Attributes
    ----------
    chat_id : int
        Unique identifier for the chat.
    title : str
        Display title for the chat.
    unread_count : int
        Count of unread messages.
    is_user : bool
        Whether the dialog represents a user.
    is_group : bool
        Whether the dialog represents a group.
    is_channel : bool
        Whether the dialog represents a channel.
    """

    chat_id: int
    title: str
    unread_count: int
    is_user: bool
    is_group: bool
    is_channel: bool


@dataclass(frozen=True)
class MessageEnvelope:
    """Serializable view of an incoming or outgoing message.

    Attributes
    ----------
    message_id : int
        Unique identifier for the message.
    chat_id : int
        Identifier for the chat the message belongs to.
    sender_id : int | None
        Identifier of the message sender.
    text : str
        Message text content.
    sent_at : datetime | None
        Timestamp for when the message was sent.
    """

    message_id: int
    chat_id: int
    sender_id: int | None
    text: str
    sent_at: datetime | None


class TelegramClientProtocol(Protocol):
    """Protocol for the subset of Telethon used by the service."""

    async def start(self, *args: object, **kwargs: object) -> object:
        """Start the client session.

        Parameters
        ----------
        *args : object
            Positional arguments forwarded to Telethon.
        **kwargs : object
            Keyword arguments forwarded to Telethon.

        Returns
        -------
        object
            Result of the start operation.
        """

    async def disconnect(self) -> None:
        """Disconnect the client.

        Returns
        -------
        None
            Closes the client connection.
        """

    async def get_dialogs(self) -> Iterable[object]:
        """Fetch dialogs for the authenticated user.

        Returns
        -------
        Iterable[object]
            Dialog entries returned by Telethon.
        """

    async def send_message(self, entity: int, message: str) -> object:
        """Send a Telegram message.

        Parameters
        ----------
        entity : int
            Telegram chat identifier.
        message : str
            Message content to send.

        Returns
        -------
        object
            Raw message instance returned by Telethon.
        """

    async def get_messages(self, entity: int, limit: int) -> Iterable[object]:
        """Fetch recent messages.

        Parameters
        ----------
        entity : int
            Telegram chat identifier.
        limit : int
            Maximum number of messages to fetch.

        Returns
        -------
        Iterable[object]
            Messages returned by Telethon.
        """

    def add_event_handler(self, callback: object, event: object) -> None:
        """Register an event handler.

        Parameters
        ----------
        callback : object
            Callable invoked for the event.
        event : object
            Event class or instance.
        """


@dataclass
class TelegramConfig:
    """Configuration values for Telethon.

    Attributes
    ----------
    api_id : int
        Telegram API ID from https://my.telegram.org.
    api_hash : str
        Telegram API hash from https://my.telegram.org.
    session_name : str
        Local session filename used by Telethon.
    """

    api_id: int
    api_hash: str
    session_name: str = "tgui"


class TelegramService:
    """Thin wrapper around a Telethon client instance."""

    def __init__(
        self,
        config: TelegramConfig,
        client: TelegramClientProtocol | None = None,
    ) -> None:
        """Initialize the Telegram service.

        Parameters
        ----------
        config : TelegramConfig
            Configuration for the Telethon client.
        client : TelegramClientProtocol | None
            Optional client override, intended for testing.
        """
        self._client: TelegramClientProtocol = client or TelegramClient(
            config.session_name,
            config.api_id,
            config.api_hash,
        )

    async def start(
        self,
        *,
        phone: str | None = None,
        code_callback: Callable[[], str] | None = None,
        password: str | None = None,
        bot_token: str | None = None,
    ) -> None:
        """Start the Telethon client session.

        Parameters
        ----------
        phone : str | None
            Phone number for user authentication.
        code_callback : Callable[[], str] | None
            Callback returning the login code.
        password : str | None
            Two-factor authentication password.
        bot_token : str | None
            Bot token for bot authentication.

        Returns
        -------
        None
            Starts the connection and handles authorization.
        """
        await self._client.start(
            phone=phone,
            code_callback=code_callback,
            password=password,
            bot_token=bot_token,
        )

    async def disconnect(self) -> None:
        """Disconnect the Telethon client session."""
        await self._client.disconnect()

    @property
    def client(self) -> TelegramClientProtocol:
        """Return the raw Telethon client instance."""
        return self._client

    async def dialogs(self) -> list[ChatSummary]:
        """Fetch chat dialogs for the authenticated user.

        Returns
        -------
        list[ChatSummary]
            Summaries of the user's dialogs.
        """
        dialogs = await self._client.get_dialogs()
        return [self._dialog_to_summary(dialog) for dialog in dialogs]

    async def send_message(self, chat_id: int, text: str) -> MessageEnvelope:
        """Send a message to a Telegram chat.

        Parameters
        ----------
        chat_id : int
            Telegram chat identifier.
        text : str
            Message content to send.

        Returns
        -------
        MessageEnvelope
            Serialized view of the sent message.
        """
        message = await self._client.send_message(chat_id, text)
        return self._message_to_envelope(message, chat_id_override=chat_id)

    async def recent_messages(self, chat_id: int, limit: int = 50) -> list[MessageEnvelope]:
        """Fetch recent messages for a chat.

        Parameters
        ----------
        chat_id : int
            Telegram chat identifier.
        limit : int, optional
            Maximum number of messages to return.

        Returns
        -------
        list[MessageEnvelope]
            Recent messages in the chat.
        """
        messages = await self._client.get_messages(chat_id, limit=limit)
        return [self._message_to_envelope(message, chat_id_override=chat_id) for message in messages]

    def add_message_listener(self, handler: MessageHandler) -> None:
        """Register a handler for incoming messages.

        Parameters
        ----------
        handler : MessageHandler
            Callback invoked for each new message.
        """

        async def _wrapper(event: events.NewMessage.Event) -> None:
            envelope = self._message_to_envelope(event.message)
            await handler(envelope)

        self._client.add_event_handler(_wrapper, events.NewMessage())

    def _dialog_to_summary(self, dialog: object) -> ChatSummary:
        """Convert a Telethon dialog to a summary."""
        return ChatSummary(
            chat_id=int(getattr(dialog, "id")),
            title=str(getattr(dialog, "title", "")),
            unread_count=int(getattr(dialog, "unread_count", 0)),
            is_user=bool(getattr(dialog, "is_user", False)),
            is_group=bool(getattr(dialog, "is_group", False)),
            is_channel=bool(getattr(dialog, "is_channel", False)),
        )

    def _message_to_envelope(
        self,
        message: object,
        *,
        chat_id_override: int | None = None,
    ) -> MessageEnvelope:
        """Convert a Telethon message to a serializable envelope."""
        chat_id_value = chat_id_override
        if chat_id_value is None:
            chat_id_value = int(getattr(message, "chat_id", 0))
        return MessageEnvelope(
            message_id=int(getattr(message, "id", 0)),
            chat_id=chat_id_value,
            sender_id=getattr(message, "sender_id", None),
            text=str(getattr(message, "message", "")),
            sent_at=getattr(message, "date", None),
        )
