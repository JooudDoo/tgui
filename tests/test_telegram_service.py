from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from tgui.telegram.client import MessageEnvelope, TelegramConfig, TelegramService


@dataclass
class FakeDialog:
    id: int
    title: str
    unread_count: int
    is_user: bool
    is_group: bool
    is_channel: bool


@dataclass
class FakeMessage:
    id: int
    chat_id: int
    sender_id: int | None
    message: str
    date: datetime


class FakeEvent:
    def __init__(self, message: FakeMessage) -> None:
        self.message = message


class FakeClient:
    def __init__(self) -> None:
        self.dialogs: list[FakeDialog] = []
        self.messages: list[FakeMessage] = []
        self.send_response: FakeMessage | None = None
        self.started: dict[str, object] | None = None
        self.sent: tuple[int, str] | None = None
        self.get_messages_args: tuple[int, int] | None = None
        self.added_handlers: list[tuple[Callable[[object], Awaitable[None]], object]] = []

    async def start(self, *args: object, **kwargs: object) -> object:
        self.started = {"args": args, "kwargs": kwargs}
        return None

    async def disconnect(self) -> None:
        return None

    async def get_dialogs(self) -> list[FakeDialog]:
        return self.dialogs

    async def send_message(self, entity: int, message: str) -> FakeMessage:
        self.sent = (entity, message)
        if self.send_response is None:
            raise AssertionError("send_response not set")
        return self.send_response

    async def get_messages(self, entity: int, limit: int) -> list[FakeMessage]:
        self.get_messages_args = (entity, limit)
        return self.messages

    def add_event_handler(
        self,
        callback: Callable[[object], Awaitable[None]],
        event: object,
    ) -> None:
        self.added_handlers.append((callback, event))


@pytest.mark.asyncio
async def test_dialogs_returns_summaries() -> None:
    fake_client = FakeClient()
    fake_client.dialogs = [
        FakeDialog(1, "Chat 1", 2, True, False, False),
        FakeDialog(2, "Chat 2", 0, False, True, False),
    ]
    service = TelegramService(
        TelegramConfig(api_id=1, api_hash="hash"),
        client=fake_client,
    )

    dialogs = await service.dialogs()

    assert [dialog.chat_id for dialog in dialogs] == [1, 2]
    assert dialogs[0].title == "Chat 1"
    assert dialogs[1].is_group is True


@pytest.mark.asyncio
async def test_send_message_maps_response() -> None:
    fake_client = FakeClient()
    fake_client.send_response = FakeMessage(
        id=10,
        chat_id=99,
        sender_id=42,
        message="Hello",
        date=datetime(2024, 1, 1, tzinfo=UTC),
    )
    service = TelegramService(
        TelegramConfig(api_id=1, api_hash="hash"),
        client=fake_client,
    )

    envelope = await service.send_message(99, "Hello")

    assert fake_client.sent == (99, "Hello")
    assert envelope == MessageEnvelope(
        message_id=10,
        chat_id=99,
        sender_id=42,
        text="Hello",
        sent_at=fake_client.send_response.date,
    )


@pytest.mark.asyncio
async def test_recent_messages_maps_messages() -> None:
    fake_client = FakeClient()
    fake_client.messages = [
        FakeMessage(
            id=1,
            chat_id=7,
            sender_id=8,
            message="Ping",
            date=datetime(2024, 2, 1, tzinfo=UTC),
        )
    ]
    service = TelegramService(
        TelegramConfig(api_id=1, api_hash="hash"),
        client=fake_client,
    )

    messages = await service.recent_messages(7, limit=1)

    assert fake_client.get_messages_args == (7, 1)
    assert messages[0].text == "Ping"
    assert messages[0].chat_id == 7


@pytest.mark.asyncio
async def test_add_message_listener_registers_handler() -> None:
    fake_client = FakeClient()
    service = TelegramService(
        TelegramConfig(api_id=1, api_hash="hash"),
        client=fake_client,
    )
    received: list[MessageEnvelope] = []

    async def handler(envelope: MessageEnvelope) -> None:
        received.append(envelope)

    service.add_message_listener(handler)

    assert len(fake_client.added_handlers) == 1
    callback, _event = fake_client.added_handlers[0]
    message = FakeMessage(
        id=5,
        chat_id=77,
        sender_id=9,
        message="Incoming",
        date=datetime(2024, 3, 1, tzinfo=UTC),
    )
    await callback(FakeEvent(message))

    assert received[0].message_id == 5
    assert received[0].chat_id == 77
