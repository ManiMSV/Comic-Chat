import type { ComicInstruction } from "@/client"

import { PANEL_HEIGHT, PANEL_WIDTH } from "./geometry"
import Panel from "./Panel"

interface ComicStripProps {
  comic: ComicInstruction
}

const ComicStrip = ({ comic }: ComicStripProps) => {
  const panelCount = comic.panels.length
  const totalHeight = panelCount * PANEL_HEIGHT

  return (
    <svg
      viewBox={`0 0 ${PANEL_WIDTH} ${totalHeight}`}
      width="100%"
      role="img"
      aria-label="Comic strip"
    >
      <title>Comic strip</title>
      {comic.panels.map((panel, index) => (
        <g
          key={panel.messages[0]?.id ?? index}
          transform={`translate(0, ${index * PANEL_HEIGHT})`}
        >
          <Panel
            panel={panel}
            characters={comic.characters}
            index={index + 1}
          />
        </g>
      ))}
    </svg>
  )
}

export default ComicStrip
