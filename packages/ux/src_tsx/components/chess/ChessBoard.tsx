import Box from "@mui/material/Box";
import { memo, type ReactElement } from "react";

import type { SquareKey, SquareView } from "../../chess/chess_views";
import { ChessSquare } from "./ChessSquare";
import { useBoardSkin } from "./skins/board_skin_context";

const SQUARES_SX = {
  display: "grid",
  gridTemplateColumns: "repeat(8, minmax(0, 1fr))",
  width: "100%",
  aspectRatio: "1 / 1",
} as const;

export type ChessBoardProps = {
  readonly squares: readonly SquareView[];
  readonly fileLetters: readonly string[];
  readonly rankDigits: readonly string[];
  readonly onSelect: (squareKey: SquareKey) => void;
};

/**
 * Sixty-four squares in the order they are drawn, inside the skin's frame.
 */
export const ChessBoard = memo(function ChessBoard(props: ChessBoardProps): ReactElement {
  const { squares, fileLetters, rankDigits, onSelect } = props;
  const { skin } = useBoardSkin();
  const Frame = skin.Board;

  const cells = squares.map((square: SquareView) => (
    <ChessSquare
      key={square.key}
      squareKey={square.key}
      label={square.label}
      isLight={square.isLight}
      occupant={square.occupant}
      isSelected={square.isSelected}
      isSelectable={square.isSelectable}
      isLegalTarget={square.isLegalTarget}
      isCaptureTarget={square.isCaptureTarget}
      isLastMove={square.isLastMove}
      isCheckedKing={square.isCheckedKing}
      onSelect={onSelect}
    />
  ));

  return (
    <Frame fileLetters={fileLetters} rankDigits={rankDigits}>
      <Box sx={SQUARES_SX} role="grid" aria-label="Chess board">
        {cells}
      </Box>
    </Frame>
  );
});
