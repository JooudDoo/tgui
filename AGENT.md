1) Core Architecture (Modules & Responsibilities)
A. Telegram Protocol Layer
Goal: Abstract MTProto access, updates, and file upload/download.

Options:

Telethon (recommended): Mature MTProto client, async-first, supports messages, reactions, files, replies, edits, media, dialogs.

Pyrogram: Also good, simpler API; slightly less flexible.

TDLib via python-tdlib: More heavy but feature-complete; requires external binary.

Recommendation: Telethon for speed + flexibility.

Module structure:

tgui/telegram/client.py — thin wrapper over Telethon session + auth flow

tgui/telegram/updates.py — update handlers (new messages, edits, reactions)

tgui/telegram/media.py — file upload/download helpers

B. Application Core
Goal: App state + orchestration.

tgui/core/state.py — in-memory state (current chat, selection, view mode)

tgui/core/events.py — internal event bus (e.g., “message_received”)

tgui/core/actions.py — send message, reply, react, send file

This layer should not depend on the UI; UI dispatches actions into core.

C. Storage Layer
Goal: Caching + persistence.

SQLite + SQLModel or SQLite + aiosqlite

Cache dialogs, messages, media metadata, download state.

Possibly skip full message history and rely on Telegram APIs + limited cache.

Module:

tgui/storage/db.py

tgui/storage/models.py

tgui/storage/cache.py

D. Media Processing Pipeline
Goal: Download, cache, render images/stickers.

Images

Pillow for decoding (JPEG/PNG/WebP).

Convert to terminal-friendly format.

Terminal image output options:

Kitty graphics protocol (best experience, fast): use kitty or term-image.

iTerm2 protocol (macOS).

Sixel (xterm compatible).

Fallback to ASCII blocks (e.g., rich or custom).

Stickers

Many stickers are .webp or .tgs (Lottie).

.webp -> Pillow works.

.tgs (Lottie JSON) requires rlottie or lottie Python libs; may need native dependency.

Initially: support static stickers first; animate later.

Module:

tgui/media/decoder.py

tgui/media/renderers/{kitty,iterm,sixel,ascii}.py

tgui/media/cache.py

E. TUI (Terminal UI)
Goal: Chat views, input box, dialogs list, mouse support.

Options:

Textual (recommended): modern TUI, mouse support, async-friendly.

Urwid: older but stable.

Prompt_toolkit: good for input, less for multi-pane UI.

Recommendation: Textual for layout + mouse support.

UI structure:

Left pane: chats list

Right pane: message history + inline media

Bottom: input + status bar

Optional: preview pane for media

Module:

tgui/ui/app.py

tgui/ui/widgets/ (ChatList, MessageView, InputBox, MediaView)

2) Feature Coverage Mapping
Feature	Implementation Notes
Images	Download via Telethon, decode with Pillow, render with terminal protocol
Stickers	WebP via Pillow; .tgs later via Lottie/rlottie
Reactions	Telethon supports reactions (MessageReaction)
Replies	Store reply_to message and render inline
Files	Telethon send_file / download_media
Mouse	Textual mouse events (click to select messages/chats)
Videos	Not “playable” in terminal; show thumbnail + open external player
Read/typing	Telegram updates allow typing indicators + read states
3) CLI + Packaging with uv
Structure:

pyproject.toml with dependencies

Use uv for fast install + lock

Example deps:

telethon
textual
pillow
rich
aiosqlite
term-image   # optional
4) Possible MVP Roadmap
Phase 1

Auth + list dialogs

Read and send text messages

Basic replies

Simple UI layout

Minimal caching

Phase 2

Images + static stickers

Reactions

File sending

Mouse clicks

Phase 3

Animated stickers (.tgs)

Rich previews

Video thumbnails + external open

Profile photos, emojis rendering

5) Notes on Terminal Media Support
Terminal image support depends on the emulator:

Kitty: best quality, easiest

iTerm2: good on macOS

Sixel: old but works on many terminals

Fallback: ASCII/Unicode blocks

We can detect terminal capabilities and switch renderer.
- Use concise NumPy-style docstrings for all public functions, methods, and classes.
- Keep comments brief and meaningful.
- Prefer clear, testable boundaries and add tests for new logic.
- Run ruff, pyright, and pytest before shipping changes.
- Check ruff and pyright before submitting code and fix any reported issues.
- Before submitting, run the app and confirm the main flows work.
