"""State container for the tgui application."""

from __future__ import annotations

from dataclasses import dataclass, field

from tgui.telegram.client import ChatSummary


@dataclass
class AppState:
    """In-memory UI/application state.

    Attributes
    ----------
    active_chat_id : int | None
        Identifier for the active chat, if any.
    chats : list[ChatSummary]
        Cached list of chats.
    draft_message : str
        Current input buffer for the message composer.
    """

    active_chat_id: int | None = None
    chats: list[ChatSummary] = field(default_factory=list)
    draft_message: str = ""
