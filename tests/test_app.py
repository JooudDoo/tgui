import pytest

from tgui.ui.app import TguiApp


@pytest.mark.asyncio
async def test_app_mounts_auth_screen(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TGUI_API_ID", "123")
    monkeypatch.setenv("TGUI_API_HASH", "hash")
    monkeypatch.setenv("TGUI_SESSION_NAME", "session")

    app = TguiApp()
    async with app.run_test():
        assert app.get_screen("auth") is not None
