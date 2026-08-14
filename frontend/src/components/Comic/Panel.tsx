import type { Character, Panel as ComicPanel } from "@/client"

import Balloon from "./Balloon"
import CharacterFigure from "./Character"
import {
  BALLOON_GAP,
  BALLOON_START_Y,
  BALLOON_WIDTH,
  BALLOON_X_LEFT,
  BALLOON_X_RIGHT,
  balloonHeight,
  CHARACTER_X_LEFT,
  CHARACTER_X_RIGHT,
  PANEL_HEIGHT,
  PANEL_WIDTH,
  wrapText,
} from "./geometry"

interface PanelProps {
  panel: ComicPanel
  characters: Character[]
  index: number
}

const Panel = ({ panel, characters, index }: PanelProps) => {
  const characterMap = new Map(
    characters.map((character) => [character.id, character]),
  )
  const names = panel.characters
    .map(
      (placement) =>
        characterMap.get(placement.character_id)?.name ??
        placement.character_id,
    )
    .join(" and ")
  const characterX = (side: "left" | "right") =>
    side === "left" ? CHARACTER_X_LEFT : CHARACTER_X_RIGHT
  const balloonX = (side: "left" | "right") =>
    side === "left" ? BALLOON_X_LEFT : BALLOON_X_RIGHT

  return (
    <g aria-label={`Panel ${index}: ${names}`}>
      <title>{`Panel ${index}: ${names}`}</title>
      <rect
        x={0}
        y={0}
        width={PANEL_WIDTH}
        height={PANEL_HEIGHT}
        rx={8}
        fill="#ffffff"
        stroke="#e2e8f0"
        strokeWidth={2}
      />
      {panel.characters.map((placement) => {
        const character = characterMap.get(placement.character_id)
        if (!character) {
          return null
        }
        const x = characterX(placement.side)
        const balloons = panel.messages.filter(
          (message) => message.speaker_id === placement.character_id,
        )
        let y = BALLOON_START_Y
        return (
          <g key={placement.character_id}>
            <CharacterFigure character={character} x={x} />
            {balloons.map((message) => {
              const lines = wrapText(message.text)
              const height = balloonHeight(lines)
              const balloon = (
                <Balloon
                  key={message.id}
                  message={message}
                  palette={character.palette}
                  x={balloonX(placement.side)}
                  y={y}
                  width={BALLOON_WIDTH}
                  lines={lines}
                  side={placement.side}
                />
              )
              y += height + BALLOON_GAP
              return balloon
            })}
          </g>
        )
      })}
    </g>
  )
}

export default Panel
