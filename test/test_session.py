import json
from pathlib import Path

from src.wip.session.session import Session


def test_session_tracks_messages_and_can_save_load(tmp_path):
    session = Session()

    session.add_user_message("hello")
    session.add_agent_message("hi there")

    assert session.messages == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi there"},
    ]

    path = tmp_path / "session.json"
    session.save(path)

    reloaded = Session.load(path)
    assert reloaded.messages == session.messages
