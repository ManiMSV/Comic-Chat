"""Unit tests for the composer orchestration (T006/T013, constitution principles II/IV)."""

import inspect
import re

import pytest

from app.schemas.comic import ComicInstruction, ComicMessage, Expression
from app.services import composer
from app.services.analyzer import resolve_expression

DB_OR_HTTP_IMPORT_RE = re.compile(
    r"^\s*(from app\.core\.(db|config)|"
    r"import (httpx|requests|fastapi|sqlmodel)|"
    r"from (fastapi|sqlmodel|httpx|requests))\b",
    re.MULTILINE,
)


def test_compose_is_callable() -> None:
    assert callable(composer.compose)


def test_compose_signature_is_typed_boundary() -> None:
    signature = inspect.signature(composer.compose)
    assert list(signature.parameters) == ["messages"]
    assert signature.parameters["messages"].annotation == list[ComicMessage]
    assert signature.return_annotation is ComicInstruction


def test_composer_module_has_no_db_or_http_imports() -> None:
    source = inspect.getsource(composer)
    assert not DB_OR_HTTP_IMPORT_RE.search(source)


def test_compose_returns_typed_instruction_for_valid_conversation() -> None:
    instruction = composer.compose(
        [
            ComicMessage(speaker_id="ada", text="wow, whoa, look at that!"),
            ComicMessage(speaker_id="bob", text="oh my, what a find!"),
        ]
    )
    assert isinstance(instruction, ComicInstruction)
    assert len(instruction.panels) >= 1
    assert len(instruction.characters) == 3
    assert all(panel.messages for panel in instruction.panels)


def test_compose_raises_value_error_on_unknown_speaker() -> None:
    with pytest.raises(ValueError, match="unknown speaker_id"):
        composer.compose([ComicMessage(speaker_id="nope", text="hello")])


def test_compose_wires_resolved_expression_into_rendered_messages() -> None:
    messages = [
        ComicMessage(speaker_id="ada", text="yay, we found it!"),
        ComicMessage(speaker_id="bob", text="I HATE THIS SO MUCH"),
        ComicMessage(speaker_id="ada", text="hello there"),
    ]
    instruction = composer.compose(messages)
    rendered = [message for panel in instruction.panels for message in panel.messages]
    assert [message.expression for message in rendered] == [
        Expression.joy,
        Expression.anger,
        Expression.neutral,
    ]
    for message, source in zip(rendered, messages, strict=True):
        assert message.expression is resolve_expression(source.text)
