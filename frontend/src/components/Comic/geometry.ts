export const PANEL_WIDTH = 320
export const PANEL_HEIGHT = 260
export const CHARACTER_X_LEFT = 70
export const CHARACTER_X_RIGHT = 250
export const CHARACTER_HEAD_CY = 215
export const BALLOON_X_LEFT = 12
export const BALLOON_X_RIGHT = 172
export const BALLOON_WIDTH = 136
export const BALLOON_START_Y = 14
export const BALLOON_GAP = 6
export const MAX_CHARS_PER_LINE = 18
const LINE_HEIGHT = 12
const BALLOON_PADDING_Y = 8

export function wrapText(
  text: string,
  maxChars: number = MAX_CHARS_PER_LINE,
): string[] {
  const words = text.split(/\s+/)
  const lines: string[] = []
  let current = ""
  for (const word of words) {
    if (current === "") {
      current = word
    } else if (`${current} ${word}`.length <= maxChars) {
      current = `${current} ${word}`
    } else {
      lines.push(current)
      current = word
    }
  }
  if (current !== "") {
    lines.push(current)
  }
  return lines.length > 0 ? lines : [""]
}

export function balloonHeight(lines: string[]): number {
  return Math.max(30, lines.length * LINE_HEIGHT + BALLOON_PADDING_Y)
}
