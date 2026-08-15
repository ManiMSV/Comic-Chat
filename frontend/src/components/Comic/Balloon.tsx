import type { Palette, RenderedMessage } from "@/client"

import { balloonHeight } from "./geometry"

interface BalloonProps {
  message: RenderedMessage
  palette: Palette
  x: number
  y: number
  width: number
  lines: string[]
  side: "left" | "right"
}

function zigzagPolygon(
  x: number,
  y: number,
  width: number,
  height: number,
): string {
  const step = 10
  const amp = 2
  const points: string[] = []
  let index = 0
  for (let px = x; px <= x + width; px += step) {
    points.push(`${px},${y + (index++ % 2 === 0 ? amp : 0)}`)
  }
  for (let py = y; py <= y + height; py += step) {
    points.push(`${x + width - (index++ % 2 === 0 ? amp : 0)},${py}`)
  }
  for (let px = x + width; px >= x; px -= step) {
    points.push(`${px},${y + height - (index++ % 2 === 0 ? amp : 0)}`)
  }
  for (let py = y + height; py >= y; py -= step) {
    points.push(`${x + (index++ % 2 === 0 ? amp : 0)},${py}`)
  }
  return points.join(" ")
}

function tailPoints(
  x: number,
  y: number,
  width: number,
  height: number,
  side: "left" | "right",
): string {
  if (side === "left") {
    return `${x + 18},${y + height} ${x + 30},${y + height} ${x + 24},${y + height + 12}`
  }
  return `${x + width - 18},${y + height} ${x + width - 30},${y + height} ${x + width - 24},${y + height + 12}`
}

const Balloon = ({
  message,
  palette,
  x,
  y,
  width,
  lines,
  side,
}: BalloonProps) => {
  const height = balloonHeight(lines)
  const isShout = message.balloon === "shout"
  const fill = palette.secondary
  const stroke = isShout ? palette.primary : palette.accent
  const textY = y + 13

  return (
    <g>
      <polygon
        points={tailPoints(x, y, width, height, side)}
        fill={fill}
        stroke={stroke}
        strokeWidth={isShout ? 2.5 : 1.5}
      />
      {isShout ? (
        <polygon
          points={zigzagPolygon(x, y, width, height)}
          fill={fill}
          stroke={palette.primary}
          strokeWidth={2.5}
        />
      ) : (
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          rx={14}
          fill={fill}
          stroke={palette.accent}
          strokeWidth={1.5}
        />
      )}
      {lines.map((line, index) => (
        <text
          key={line + index}
          x={x + 8}
          y={textY + index * 12}
          fontSize={10}
          fill={palette.accent}
        >
          {line}
        </text>
      ))}
    </g>
  )
}

export default Balloon
