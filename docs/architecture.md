# Architecture plan

## Goals

- Terminal-first Telegram client with images, stickers, reactions, replies, and file sending.
- Easy setup for contributors and end users via `uv`.

## Proposed stack

- **MTProto client:** Telethon
- **TUI framework:** Textual (mouse support, async friendly)
- **Storage:** SQLite + aiosqlite
- **Media:** Pillow for decoding + optional terminal renderers (Kitty/iTerm2/Sixel)

## Modules

- `tgui/telegram/` — Telethon session, updates, and media helpers
- `tgui/core/` — state, actions, and event wiring
- `tgui/ui/` — Textual widgets and layout
- `tgui/media/` — decoding and terminal renderers
- `tgui/storage/` — cache and persistence

## Milestones

1. Auth + list chats + read/send text
2. Replies + reactions + file sending
3. Images + static stickers, terminal image protocol detection
4. Animated stickers (Lottie) + media previews
