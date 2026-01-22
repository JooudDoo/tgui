"""SQLite helpers for tgui storage."""

from __future__ import annotations

import aiosqlite


async def open_db(path: str) -> aiosqlite.Connection:
    """Open a SQLite database connection.

    Parameters
    ----------
    path : str
        Path to the SQLite database file.

    Returns
    -------
    aiosqlite.Connection
        An active connection to the database.
    """
    return await aiosqlite.connect(path)
