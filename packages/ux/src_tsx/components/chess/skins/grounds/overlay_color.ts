import type { BoardSkinPalette, SquareGroundProps } from "../board_skin";

/**
 * The one overlay a square shows, or null. A king in check is marked before
 * anything else, so the danger is never hidden by a selection.
 */
export function overlayColorOf(props: SquareGroundProps, palette: BoardSkinPalette): string | null {
  if (props.isCheckedKing) {
    return palette.checkOverlay;
  }
  if (props.isSelected) {
    return palette.selectedOverlay;
  }
  if (props.isLastMove) {
    return palette.lastMoveOverlay;
  }
  return null;
}
