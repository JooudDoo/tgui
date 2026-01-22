"""Telegram integration powered by Telethon."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, TypeAlias

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

    def start(
        self,
        phone: Callable[[], str] | str = ...,
        password: Callable[[], str] | str = ...,
        *,
        bot_token: str = "",
        force_sms: bool = False,
        code_callback: Callable[[], str | int] | None = None,
        first_name: str = "New User",
        last_name: str = "",
        max_attempts: int = 3,
    ) -> object | Awaitable[object] | None:
        """Start the client session.

        Parameters
        ----------
        phone : Callable[[], str] | str, optional
            Phone number or callable that returns it.
        password : Callable[[], str] | str, optional
            Password or callable that returns it.
        bot_token : str, optional
            Bot token to authenticate as a bot.
        force_sms : bool, optional
            Force SMS verification.
        code_callback : Callable[[], str | int] | None, optional
            Callback returning the login code.
        first_name : str, optional
            Default first name for signup flows.
        last_name : str, optional
            Default last name for signup flows.
        max_attempts : int, optional
            Maximum login attempts.

        Returns
        -------
        object | Awaitable[object]
            Result of the start operation.
        """
        ...

    async def disconnect(self) -> None:
        """Disconnect the client.

        Returns
        -------
        None
            Closes the client connection.
        """
        ...

    async def get_dialogs(self) -> Iterable[DialogProtocol]:
        """Fetch dialogs for the authenticated user.

        Returns
        -------
        Iterable[object]
            Dialog entries returned by Telethon.
        """
        ...

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
        ...

    async def get_messages(
        self,
        entity: int,
        limit: int,
    ) -> Iterable[object] | object | None:
        """Fetch recent messages.

        Parameters
        ----------
        entity : int
            Telegram chat identifier.
        limit : int
            Maximum number of messages to fetch.

        Returns
        -------
        Iterable[object] | object | None
            Messages returned by Telethon.
        """
        ...

    def add_event_handler(
        self,
        callback: Callable[..., Awaitable[None]],
        event: object | None = None,
    ) -> None:
        """Register an event handler.

        Parameters
        ----------
        callback : Callable[[object], Awaitable[None]]
            Callable invoked for the event.
        event : object
            Event class or instance.
        """
        ...


class DialogProtocol(Protocol):
    """Protocol for the dialog attributes used in summaries."""

    id: int
    title: str
    unread_count: int
    is_user: bool
    is_group: bool
    is_channel: bool


TelegramClientLike: TypeAlias = TelegramClientProtocol | TelegramClient


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
        client: TelegramClientLike | None = None,
    ) -> None:
        """Initialize the Telegram service.

        Parameters
        ----------
        config : TelegramConfig
            Configuration for the Telethon client.
        client : TelegramClientLike | None
            Optional client override, intended for testing.
        """
        self._client: TelegramClientLike = client or TelegramClient(
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
        if code_callback is None:
            result = self._client.start(
                phone=phone or "",
                password=password or "",
                bot_token=bot_token or "",
            )
        else:
            result = self._client.start(
                phone=phone or "",
                password=password or "",
                bot_token=bot_token or "",
                code_callback=code_callback,
            )
        if isinstance(result, Awaitable):
            await result

    async def disconnect(self) -> None:
        """Disconnect the Telethon client session."""
        await self._client.disconnect()

    @property
    def client(self) -> TelegramClientLike:
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
        normalized = self._normalize_messages(messages)
        return [
            self._message_to_envelope(message, chat_id_override=chat_id)
            for message in normalized
        ]

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

    def _dialog_to_summary(self, dialog: DialogProtocol) -> ChatSummary:
        """Convert a Telethon dialog to a summary."""
        return ChatSummary(
            chat_id=int(dialog.id),
            title=str(dialog.title),
            unread_count=int(dialog.unread_count),
            is_user=bool(dialog.is_user),
            is_group=bool(dialog.is_group),
            is_channel=bool(dialog.is_channel),
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

    def _normalize_messages(self, messages: Iterable[object] | object | None) -> list[object]:
        """Normalize Telethon message responses into a list.

        Parameters
        ----------
        messages : Iterable[object] | object | None
            Raw messages from the client.

        Returns
        -------
        list[object]
            Normalized message list.
        """
        if messages is None:
            return []
        if isinstance(messages, Iterable):
            return list(messages)
        return [messages]
