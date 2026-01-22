"""State container for the tgui application."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppState:
    """In-memory UI/application state.

    Attributes
    ----------
    active_chat_id : int | None
        Identifier for the active chat, if any.
    draft_message : str
        Current input buffer for the message composer.
    """

    active_chat_id: int | None = None
    draft_message: str = ""
