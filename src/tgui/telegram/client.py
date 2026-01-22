"""Telegram integration powered by Telethon."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from telethon import TelegramClient


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
    """Thin wrapper around a Telethon client instance.

    Parameters
    ----------
    config : TelegramConfig
        Configuration for the Telethon client.
    """

    def __init__(self, config: TelegramConfig) -> None:
        self._client = TelegramClient(config.session_name, config.api_id, config.api_hash)

    async def start(self) -> None:
        """Start the Telethon client session.

        Returns
        -------
        None
            Starts the connection and handles authorization.
        """
        await self._client.start()

    async def disconnect(self) -> None:
        """Disconnect the Telethon client session."""
        await self._client.disconnect()

    @property
    def client(self) -> TelegramClient:
        """Return the raw Telethon client instance."""
        return self._client

    async def dialogs(self) -> Iterable[object]:
        """Fetch dialogs for the authenticated user.

        Returns
        -------
        Iterable[object]
            Dialog entries returned by Telethon.
        """
        return await self._client.get_dialogs()
