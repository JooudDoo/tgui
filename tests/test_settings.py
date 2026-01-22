import pytest

from tgui.core.settings import AppSettings, load_settings


def test_load_settings_from_env() -> None:
    settings = load_settings(
        {
            "TGUI_API_ID": "123",
            "TGUI_API_HASH": "hash",
            "TGUI_SESSION_NAME": "session",
        }
    )

    assert settings == AppSettings(api_id=123, api_hash="hash", session_name="session")


def test_load_settings_requires_values() -> None:
    with pytest.raises(ValueError, match="TGUI_API_ID and TGUI_API_HASH"):
        load_settings({})


def test_load_settings_requires_integer_api_id() -> None:
    with pytest.raises(ValueError, match="TGUI_API_ID must be an integer"):
        load_settings({"TGUI_API_ID": "abc", "TGUI_API_HASH": "hash"})
