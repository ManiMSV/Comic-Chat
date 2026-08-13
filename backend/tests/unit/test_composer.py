"""Unit tests for the composer skeleton (T006, constitution principles II/IV)."""

import inspect
import re

import pytest

from app.schemas.comic import ComicInstruction, ComicMessage
from app.services import composer

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


def test_compose_raises_until_orchestration_lands() -> None:
    with pytest.raises(NotImplementedError, match="T013"):
        composer.compose([ComicMessage(speaker_id="ada", text="hello")])