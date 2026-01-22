"""Settings helpers for tgui."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from tgui.telegram.client import TelegramConfig


@dataclass(frozen=True)
class AppSettings:
    """Application settings for Telegram access.

    Attributes
    ----------
    api_id : int
        Telegram API ID.
    api_hash : str
        Telegram API hash.
    session_name : str
        Telethon session name.
    """

    api_id: int
    api_hash: str
    session_name: str = "tgui"

    def to_telegram_config(self) -> TelegramConfig:
        """Convert settings into a TelegramConfig.

        Returns
        -------
        TelegramConfig
            Config object for the Telegram client.
        """
        return TelegramConfig(
            api_id=self.api_id,
            api_hash=self.api_hash,
            session_name=self.session_name,
        )


def load_settings(environ: Mapping[str, str]) -> AppSettings:
    """Load application settings from environment variables.

    Parameters
    ----------
    environ : Mapping[str, str]
        Environment mapping to read from.

    Returns
    -------
    AppSettings
        Parsed settings values.

    Raises
    ------
    ValueError
        If required settings are missing or invalid.
    """
    api_id_raw = environ.get("TGUI_API_ID")
    api_hash = environ.get("TGUI_API_HASH")
    session_name = environ.get("TGUI_SESSION_NAME", "tgui")

    if not api_id_raw or not api_hash:
        raise ValueError("TGUI_API_ID and TGUI_API_HASH are required")

    try:
        api_id = int(api_id_raw)
    except ValueError as exc:
        raise ValueError("TGUI_API_ID must be an integer") from exc

    return AppSettings(api_id=api_id, api_hash=api_hash, session_name=session_name)
