# Architecture plan

## Goals

- Terminal-first Telegram client with images, stickers, reactions, replies, and file sending.
- Easy setup for contributors and end users via `uv`.

## Current state

- Minimal Textual shell renders a placeholder screen.
- Telethon client wrapper, state/actions, storage helper, and image decoder stubs exist.
- Ruff and Pyright configurations are in place for linting and type checking.

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

## Next version (proposed)

1. Add configuration loading for API ID/hash and session path.
2. Implement login flow + dialog list rendering in the UI.
3. Add basic message list view with send/reply actions.
