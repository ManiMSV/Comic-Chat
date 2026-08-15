import type { ReactNode } from "react"

import type { Character as CharacterSpec } from "@/client"

import { CHARACTER_HEAD_CY } from "./geometry"

interface CharacterProps {
  character: CharacterSpec
  x: number
}

const HEAD_RADIUS = 18
const HEAD_Y_OFFSET = 18

function headShape(character: CharacterSpec, x: number): ReactNode {
  switch (character.silhouette) {
    case "circle":
      return (
        <circle
          cx={x}
          cy={CHARACTER_HEAD_CY}
          r={HEAD_RADIUS}
          fill={character.palette.primary}
          stroke={character.palette.accent}
          strokeWidth={1.5}
        />
      )
    case "square":
      return (
        <rect
          x={x - 17}
          y={CHARACTER_HEAD_CY - 17}
          width={34}
          height={34}
          rx={4}
          fill={character.palette.primary}
          stroke={character.palette.accent}
          strokeWidth={1.5}
        />
      )
    case "triangle":
      return (
        <polygon
          points={`${x - HEAD_RADIUS},${CHARACTER_HEAD_CY + HEAD_Y_OFFSET} ${x + HEAD_RADIUS},${CHARACTER_HEAD_CY + HEAD_Y_OFFSET} ${x},${CHARACTER_HEAD_CY - HEAD_Y_OFFSET}`}
          fill={character.palette.primary}
          stroke={character.palette.accent}
          strokeWidth={1.5}
        />
      )
    default:
      return (
        <circle
          cx={x}
          cy={CHARACTER_HEAD_CY}
          r={HEAD_RADIUS}
          fill={character.palette.primary}
          stroke={character.palette.accent}
          strokeWidth={1.5}
        />
      )
  }
}

const Character = ({ character, x }: CharacterProps) => {
  return (
    <g>
      <rect
        x={x - 23}
        y={CHARACTER_HEAD_CY + 12}
        width={46}
        height={24}
        rx={10}
        fill={character.palette.secondary}
        stroke={character.palette.primary}
        strokeWidth={2}
      />
      {headShape(character, x)}
      <text
        x={x}
        y={CHARACTER_HEAD_CY + 29}
        textAnchor="middle"
        fontSize={9}
        fontWeight="bold"
        fill={character.palette.accent}
      >
        {character.name}
      </text>
    </g>
  )
}

export default Character
