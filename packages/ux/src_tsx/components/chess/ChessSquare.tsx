import Box from "@mui/material/Box";
import { memo, useCallback, type ReactElement } from "react";

import type { OccupantView, SquareKey } from "../../chess/chess_views";
import { ChessPiece } from "./ChessPiece";
import { useBoardSkin } from "./skins/board_skin_context";

const SQUARE_SX = {
  all: "unset",
  display: "block",
  position: "relative",
  width: "100%",
  aspectRatio: "1 / 1",
  boxSizing: "border-box",
  cursor: "default",
  "&:focus-visible": { outline: "2px solid", outlineColor: "secondary.main", outlineOffset: -2, zIndex: 1 },
} as const;

const CLICKABLE_SQUARE_SX = { ...SQUARE_SX, cursor: "pointer" } as const;

export type ChessSquareProps = {
  readonly squareKey: SquareKey;
  readonly label: string;
  readonly isLight: boolean;
  readonly occupant: OccupantView | null;
  readonly isSelected: boolean;
  readonly isSelectable: boolean;
  readonly isLegalTarget: boolean;
  readonly isCaptureTarget: boolean;
  readonly isLastMove: boolean;
  readonly isCheckedKing: boolean;
  readonly onSelect: (squareKey: SquareKey) => void;
};

/**
 * One square of the board: the skin's ground, the piece on it, and the click
 * that picks it up or moves to it.
 *
 * Every square reports a click; which clicks mean anything is the screen's
 * to say, from the legal moves the game listed.
 */
export const ChessSquare = memo(function ChessSquare(props: ChessSquareProps): ReactElement {
  const {
    squareKey,
    label,
    isLight,
    occupant,
    isSelected,
    isSelectable,
    isLegalTarget,
    isCaptureTarget,
    isLastMove,
    isCheckedKing,
    onSelect,
  } = props;
  const { skin } = useBoardSkin();
  const Ground = skin.Square;

  const handleClick = useCallback(() => onSelect(squareKey), [onSelect, squareKey]);

  const piece =
    occupant === null ? null : (
      <ChessPiece color={occupant.color} pieceType={occupant.pieceType} />
    );

  const isClickable = isSelectable || isLegalTarget;

  return (
    <Box
      component="button"
      type="button"
      aria-label={label}
      aria-pressed={isSelected}
      onClick={handleClick}
      sx={isClickable ? CLICKABLE_SQUARE_SX : SQUARE_SX}
    >
      <Ground
        isLight={isLight}
        isSelected={isSelected}
        isLegalTarget={isLegalTarget}
        isCaptureTarget={isCaptureTarget}
        isLastMove={isLastMove}
        isCheckedKing={isCheckedKing}
      >
        {piece}
      </Ground>
    </Box>
  );
});
