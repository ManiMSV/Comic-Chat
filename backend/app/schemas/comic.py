from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Expression(StrEnum):
    neutral = "neutral"
    joy = "joy"
    anger = "anger"
    surprise = "surprise"
    sadness = "sadness"


class BalloonShape(StrEnum):
    speech = "speech"
    shout = "shout"
    thought = "thought"


class Side(StrEnum):
    left = "left"
    right = "right"


class Palette(BaseModel):
    primary: str
    secondary: str
    accent: str


class Character(BaseModel):
    id: str
    name: str
    palette: Palette
    silhouette: str


class CharacterPlacement(BaseModel):
    character_id: str
    side: Side


class ComicMessage(BaseModel):
    speaker_id: str
    text: str = Field(max_length=500)

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("text must not be empty")
        return value


class RenderedMessage(BaseModel):
    id: str
    speaker_id: str
    text: str
    expression: Expression
    balloon: BalloonShape


class Panel(BaseModel):
    characters: list[CharacterPlacement]
    messages: list[RenderedMessage]


class ComicInstruction(BaseModel):
    characters: list[Character]
    panels: list[Panel]


class ComicRequest(BaseModel):
    messages: list[ComicMessage] = Field(min_length=1)


class ComicResponse(BaseModel):
    comic: ComicInstruction


class DemoDialogue(BaseModel):
    id: str
    name: str
    messages: list[ComicMessage]


class DemosResponse(BaseModel):
    demos: list[DemoDialogue]
