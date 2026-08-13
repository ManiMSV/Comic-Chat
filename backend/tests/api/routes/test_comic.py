"""API tests for the comic render and demos endpoints (T009, SC-002).

Pins the contracts/api.md surface: ``POST /comic/render`` returns a typed
``ComicInstruction`` and is byte-for-byte deterministic on re-render (SC-002,
deterministic message ``id``); ``GET /comic/demos`` returns the three fixed
demo dialogues in order; the documented 422 cases (empty/absent messages,
empty/whitespace text, unknown speaker_id, overlong text) are rejected.
"""

from fastapi.testclient import TestClient

from app.core.config import settings

RENDER_URL = f"{settings.API_V1_STR}/comic/render"
DEMOS_URL = f"{settings.API_V1_STR}/comic/demos"

EXPRESSIONS = {"neutral", "joy", "anger", "surprise", "sadness"}
BALLOONS = {"speech", "shout", "thought"}
SIDES = {"left", "right"}

VALID_MESSAGES = [
    {"speaker_id": "ada", "text": "wow, whoa, look at that!"},
    {"speaker_id": "bob", "text": "I DID NOT expect that."},
]


def test_render_returns_typed_instruction(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.post(
        RENDER_URL, headers=normal_user_token_headers, json={"messages": VALID_MESSAGES}
    )
    assert r.status_code == 200

    comic = r.json()["comic"]
    assert set(comic) == {"characters", "panels"}

    characters = comic["characters"]
    assert len(characters) == 3
    for character in characters:
        assert set(character) == {"id", "name", "palette", "silhouette"}
        assert set(character["palette"]) == {"primary", "secondary", "accent"}
        assert character["silhouette"] in {"circle", "square", "triangle"}

    panels = comic["panels"]
    assert len(panels) >= 1
    for panel in panels:
        assert set(panel) == {"characters", "messages"}
        for placement in panel["characters"]:
            assert set(placement) == {"character_id", "side"}
            assert placement["side"] in SIDES
        for message in panel["messages"]:
            assert set(message) == {
                "id",
                "speaker_id",
                "text",
                "expression",
                "balloon",
            }
            assert message["id"]
            assert message["expression"] in EXPRESSIONS
            assert message["balloon"] in BALLOONS


def test_render_is_byte_identical_on_reread(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    payload = {"messages": VALID_MESSAGES}
    first = client.post(RENDER_URL, headers=normal_user_token_headers, json=payload)
    second = client.post(RENDER_URL, headers=normal_user_token_headers, json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.content == second.content


def test_render_is_byte_identical_for_demo_sized_conversation(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    payload = {
        "messages": [
            {"speaker_id": "ada", "text": "I HATE THIS SO MUCH"},
            {"speaker_id": "bob", "text": "NO. JUST NO."},
        ]
    }
    first = client.post(RENDER_URL, headers=normal_user_token_headers, json=payload)
    second = client.post(RENDER_URL, headers=normal_user_token_headers, json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.content == second.content


def test_demos_returns_three_dialogues_in_fixed_order(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(DEMOS_URL, headers=normal_user_token_headers)
    assert r.status_code == 200

    demos = r.json()["demos"]
    assert [demo["id"] for demo in demos] == [
        "surprise",
        "disagreement",
        "quiet-tension",
    ]
    for demo in demos:
        assert set(demo) == {"id", "name", "messages"}
        assert demo["name"]
        assert len(demo["messages"]) >= 1
        for message in demo["messages"]:
            assert set(message) == {"speaker_id", "text"}
            assert message["speaker_id"]
            assert message["text"]


def test_render_empty_messages_is_422(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.post(
        RENDER_URL, headers=normal_user_token_headers, json={"messages": []}
    )
    assert r.status_code == 422


def test_render_absent_messages_is_422(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.post(RENDER_URL, headers=normal_user_token_headers, json={})
    assert r.status_code == 422


def test_render_empty_text_is_422(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.post(
        RENDER_URL,
        headers=normal_user_token_headers,
        json={"messages": [{"speaker_id": "ada", "text": ""}]},
    )
    assert r.status_code == 422


def test_render_whitespace_text_is_422(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.post(
        RENDER_URL,
        headers=normal_user_token_headers,
        json={"messages": [{"speaker_id": "ada", "text": "   "}]},
    )
    assert r.status_code == 422


def test_render_unknown_speaker_id_is_422(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.post(
        RENDER_URL,
        headers=normal_user_token_headers,
        json={"messages": [{"speaker_id": "nope", "text": "hello"}]},
    )
    assert r.status_code == 422


def test_render_overlong_text_is_422(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.post(
        RENDER_URL,
        headers=normal_user_token_headers,
        json={"messages": [{"speaker_id": "ada", "text": "a" * 501}]},
    )
    assert r.status_code == 422