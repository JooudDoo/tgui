# tgui

A terminal Telegram client with rich media support (images, stickers, reactions, replies, and file sending).

## Quick start (uv)

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

Run:

```bash
tgui
```

## Linting & type checking

This project uses Ruff and Pyright.

```bash
uv pip install -e ".[dev]"
ruff check .
pyright
```

If Pyright reports missing imports locally, ensure the virtual environment is active and
dependencies are installed:

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
pyright
```

### Optional media helpers

For terminal image protocols (Kitty/iTerm2/Sixel), install the optional dependency:

```bash
uv pip install -e ".[media]"
```

## Development

- Python 3.11+
- Uses Telethon for MTProto access
- Textual for the UI
- Architecture plan: see [docs/architecture.md](docs/architecture.md)
