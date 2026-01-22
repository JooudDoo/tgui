"""Action definitions for app-level intents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SendMessage:
    """Action representing a send-message intent.

    Attributes
    ----------
    chat_id : int
        Telegram chat identifier.
    text : str
        Message content to send.
    """

    chat_id: int
    text: str


@dataclass
class SendReaction:
    """Action representing a reaction intent.

    Attributes
    ----------
    chat_id : int
        Telegram chat identifier.
    message_id : int
        Telegram message identifier.
    emoji : str
        Emoji to apply as a reaction.
    """

    chat_id: int
    message_id: int
    emoji: str
